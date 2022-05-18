from flask import Response, request
from flask_restful import Resource
import json
from models import db, Comment, Post
from views import get_authorized_user_ids

class CommentListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    def post(self):
        # create a new "Comment" based on the data posted in the body 
        body = request.get_json()
        print(body)
        if not body.get('text'):
            return Response(json.dumps({"message": "'text' is required"}), mimetype="application/json", status=400)
        if not body.get('post_id'):
            return Response(json.dumps({"message": "'post_id' is required"}), mimetype="application/json", status=400)
        
        try:
            post = Post.query.get(body.get('post_id'))
        except:
            # could not convert to int
            return Response(json.dumps({"message": "id={0} is invalid".format(body.get('post_id'))}), mimetype="application/json", status=400)
        if not post:
            return Response(json.dumps({"message": "id={0} is invalid".format(body.get('post_id'))}), mimetype="application/json", status=404)

        user_ids = get_authorized_user_ids(self.current_user)
        if post.user_id not in user_ids:
            return Response(json.dumps({"message": "id={0} is invalid".format(body.get('post_id'))}), mimetype="application/json", status=404)

        # insert whatever was posted into the database
        # (also some validation)
        new_comment = Comment(
            text=body.get('text'),
            user_id=self.current_user.id, # must be a valid user_id or will throw an error
            post_id=body.get('post_id')
        )
        db.session.add(new_comment)    # issues the insert statement
        db.session.commit()         # commits the change to the database 
        return Response(json.dumps(new_comment.to_dict()), mimetype="application/json", status=201)
        
class CommentDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
  
    def delete(self, id):
        # delete "Comment" record where "id"=id
        comment = Comment.query.get(id)
        if not comment:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        if comment.user_id != self.current_user.id:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        
        Comment.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "Comment id={0} was successfully deleted.".format(id)}), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        CommentListEndpoint, 
        '/api/comments', 
        '/api/comments/',
        resource_class_kwargs={'current_user': api.app.current_user}

    )
    api.add_resource(
        CommentDetailEndpoint, 
        '/api/comments/<int:id>', 
        '/api/comments/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
