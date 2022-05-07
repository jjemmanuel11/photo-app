from flask import Response, request
from flask_restful import Resource
from models import Bookmark, db, Post
import json
from views import get_authorized_user_ids

class BookmarksListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # get all bookmarks owned by the current user
        bookmarks = Bookmark.query.filter_by(user_id = self.current_user.id).all()
        bookmarks_json = [bookmark.to_dict() for bookmark in bookmarks]
        return Response(json.dumps(bookmarks_json), mimetype="application/json", status=200)
       

    def post(self):
        # create a new "bookmark" based on the data posted in the body 
        body = request.get_json()

        if not body.get('post_id'):
            return Response(json.dumps({"message": "'post_id' is required"}), mimetype="application/json", status=400)
        
        try:
            post = Post.query.get(body.get('post_id'))
        except:
             return Response(json.dumps({"message": "post_id is invalid"}), mimetype="application/json", status=400)
        if not post:
            return Response(json.dumps({"message": "id={0} is invalid ".format(body.get('post_id'))}), mimetype="application/json", status=404)
        
        user_ids = get_authorized_user_ids(self.current_user)
        if post.user_id not in user_ids:
            return Response(json.dumps({"message": "id={0} is invalid ".format(body.get('post_id'))}), mimetype="application/json", status=404)

        bookmarks = Bookmark.query.filter_by(user_id = self.current_user.id).all()
        for bookmark in bookmarks:
            if post.id == bookmark.post_id:
                return Response(json.dumps({"message": "post_id is invalid"}), mimetype="application/json", status=400)

        new_bookmark = Bookmark(
            user_id = self.current_user.id,
            post_id = body.get('post_id')
        )
        db.session.add(new_bookmark)    # issues the insert statement
        db.session.commit()  
    
        return Response(json.dumps(new_bookmark.to_dict()), mimetype="application/json", status=201)
        

class BookmarkDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "bookmark" record where "id"=id
        print(id)
        bookmark = Bookmark.query.get(id)
        if not bookmark:
            return Response(json.dumps({"message": "id={0} is invalid ".format(id)}), mimetype="application/json", status=404)

        if bookmark.user_id != self.current_user.id:
            return Response(json.dumps({"message": "id={0} is invalid ".format(id)}), mimetype="application/json", status=404)


        Bookmark.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "comment id = {0} was deleted "}), mimetype="application/json", status=200)
        



def initialize_routes(api):
    api.add_resource(
        BookmarksListEndpoint, 
        '/api/bookmarks', 
        '/api/bookmarks/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )

    api.add_resource(
        BookmarkDetailEndpoint, 
        '/api/bookmarks/<int:id>', 
        '/api/bookmarks/<int:id>',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
