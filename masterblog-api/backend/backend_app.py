from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

# ===Swagger UI config
SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Masterblog API"}
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
# ===swagger ends

def create_data_store():
    return {
        "posts": [
            {"id": 1, "title": "First post", "content": "This is the first post."},
            {"id": 2, "title": "Second post", "content": "This is the second post."}
        ],
        "next_id": 3
    }

store = create_data_store()


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve the list of all blog posts, optionally sorted by title or content.

    Query Parameters:
        sort (optional): Field to sort by, must be 'title' or 'content'.
        direction (optional): Sort direction, must be 'asc' or 'desc'.

    Returns:
        JSON list of blog posts with status code 200,
        or error message with status code 400 if invalid parameters are given.
    """
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    if sort_field:
        if sort_field not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400

        if direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid direction. Must be 'asc' or 'desc'."}), 400

        reverse = direction == 'desc'
        sorted_posts = sorted(store['posts'], key=lambda post: post[sort_field].lower(), reverse=reverse)
        return jsonify(sorted_posts), 200

    return jsonify(store['posts']), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Add a new blog post to the list.

    Expects:
        JSON body with 'title' and 'content' fields.

    Returns:
        JSON of the newly created post with status code 201,
        or error message with status code 400 if required fields are missing.
    """
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')

    if not title or not content:
        missing = []
        if not title:
            missing.append('title')
        if not content:
            missing.append('content')
        return jsonify({'error': f'Missing field(s): {", ".join(missing)}'}), 400

    new_post = {
        'id': store['next_id'],
        'title': title,
        'content': content
    }

    store['posts'].append(new_post)
    store['next_id'] += 1

    return jsonify(new_post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a blog post by its ID.

    Args:
        post_id: The ID of the post to delete.

    Returns:
        JSON message confirming deletion with status code 200,
        or error message with status code 404 if post is not found.
    """
    for post in store['posts']:
        if post['id'] == post_id:
            store['posts'].remove(post)
            return jsonify({"message": f"Post with id {post_id} "
                                       f"has been deleted successfully."}), 200

    return jsonify({"error": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    Update a blog post by its ID.

    Args:
        post_id: The ID of the post to update.

    Expects:
        JSON body with optional 'title' and 'content'.

    Returns:
        JSON of the updated post with status code 200,
        or error message with status code 404 if post is not found.
    """
    data = request.get_json()
    for post in store['posts']:
        if post['id'] == post_id:
            post['title'] = data.get('title', post['title'])
            post['content'] = data.get('content', post['content'])
            return jsonify(post), 200

    return jsonify({"error": f"Post with id {post_id} not found."}), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search for blog posts by title or content.

    Query Parameters:
        title (optional): Substring to search for in post titles.
        content (optional): Substring to search for in post content.

    Returns:
        JSON list of matching posts with status code 200.
    """
    title_query = request.args.get('title')
    content_query = request.args.get('content')

    filtered_posts = []

    for post in store['posts']:
        matches_title = title_query and title_query.lower() in post['title'].lower()
        matches_content = content_query and content_query.lower() in post['content'].lower()

        if matches_title or matches_content:
            filtered_posts.append(post)

    return jsonify(filtered_posts), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
