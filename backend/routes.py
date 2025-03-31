from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401
import logging

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count", methods=["GET"])
def count():
    """return length of data"""
    try:
        with open(json_url, 'r') as file:
            data = json.load(file)
        return jsonify(length=len(data)), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    try:
        with open(json_url, 'r') as file:
            data = json.load(file)
        if not data:
            return jsonify({"error": "No data found"}), 404
        urls = [item['pic_url'] for item in data]
        return jsonify(urls)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500

######################################################################
# GET A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    try:
        with open(json_url, 'r') as file:
            data = json.load(file)
        if not data:
            return jsonify({"error": "No data found"}), 404
        picture = next((item for item in data if item['id'] == id), None)
        if picture is None:
            return jsonify({"error": "Picture not found"}), 404
        return jsonify(picture)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding JSON"}), 500


######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    try:
        new_picture = request.get_json()
        if not new_picture:
            return jsonify({"error": "Invalid input"}), 400

        print(f"Received new picture data: {new_picture}")

        try:
            with open(json_url, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except json.JSONDecodeError:
            return jsonify({"error": "Error decoding JSON"}), 500

        # Check for duplicates
        if any(p['id'] == new_picture['id'] for p in data):
            return jsonify({"Message": f"picture with id {new_picture['id']} already present"}), 302

        new_picture['id'] = new_picture.get('id', max(p['id'] for p in data) + 1 if data else 1)
        data.append(new_picture)

        try:
            with open(json_url, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
            return jsonify({"error": "Error saving data"}), 500

        print(f"New picture created with id {new_picture['id']}")
        return jsonify(new_picture), 201
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    try:
        updated_picture = request.get_json()
        if not updated_picture:
            return jsonify({"error": "Invalid input"}), 400

        print(f"Received updated picture data: {updated_picture}")

        try:
            with open(json_url, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            return jsonify({"error": "File not found"}), 404
        except json.JSONDecodeError:
            return jsonify({"error": "Error decoding JSON"}), 500

        # Find the picture to update
        picture = next((p for p in data if p['id'] == id), None)
        if not picture:
            return jsonify({"message": "picture not found"}), 404

        # Update the picture data
        picture.update(updated_picture)

        try:
            with open(json_url, 'w') as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")
            return jsonify({"error": "Error saving data"}), 500

        print(f"Picture with id {id} updated")
        return jsonify(picture), 200
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500

######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    try:
        with open(json_url, 'r') as file:
            data = json.load(file)

        picture = next((item for item in data if item['id'] == id), None)
        if picture is None:
            print(f"Picture with id {id} not found")
            return jsonify({"error": f"Picture with id {id} not found"}), 404

        data.remove(picture)

        with open(json_url, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"Picture with id {id} deleted")
        return '', 204
    except FileNotFoundError:
        print("File not found")
        return jsonify({"error": "File not found"}), 404
    except json.JSONDecodeError:
        print("Error decoding JSON")
        return jsonify({"error": "Error decoding JSON"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": str(e)}), 500
