from flask import Response, request
from flask_restful import Resource
from models import LikePost, db, Post
import json
from views import get_authorized_user_ids
import flask_jwt_extended

class PostLikesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def post(self):
        # create a new "like_post" based on the data posted in the body 
        body = request.get_json()
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

        # ensure that the bookmark is not a duplicate
        likes = LikePost.query.filter_by(user_id = self.current_user.id).all()
        for like in likes:
            if post.id == like.post_id:
                return Response(json.dumps({"message": "like for id={0} already exists".format(post.id)}), mimetype="application/json", status=400)
        # insert whatever was posted into the database
        # (also some validation)
        new_like = LikePost(
            user_id=self.current_user.id, # must be a valid user_id or will throw an error
            post_id=body.get('post_id')
        )
        db.session.add(new_like)    # issues the insert statement
        db.session.commit()         # commits the change to the database 
        return Response(json.dumps(new_like.to_dict()), mimetype="application/json", status=201)

class PostLikesDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def delete(self, id):
        # delete "like_post" where "id"=id
        like_post = LikePost.query.get(id)
        if not like_post:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        if like_post.user_id != self.current_user.id:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        
        LikePost.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "LikePost id={0} was successfully deleted.".format(id)}), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        PostLikesListEndpoint, 
        '/api/posts/likes', 
        '/api/posts/likes/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )

    api.add_resource(
        PostLikesDetailEndpoint, 
        '/api/posts/likes/<int:id>', 
        '/api/posts/likes/<int:id>/',
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
