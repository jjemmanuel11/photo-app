from flask import Response, request
from flask_restful import Resource
from models import Post, db, Following
from views import get_authorized_user_ids

import json

def get_path():
    return request.host_url + 'api/posts/'

class PostListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user

    def get(self): # HTTP GET
        args = request.args
        
        # Goal: limit to only user #12 (current_user)'s network
        #   - oneself
        #   - people #12 is following

        #1. Query following table
        
        # method gets all user_ids that the current user is following.
        # also includes current user id
        user_ids = get_authorized_user_ids(self.current_user)
        try:
            limit = int(args.get('limit') or 20) # 10 is the default
        except:
            # could not convert to int
            return Response(json.dumps({"message": "the limit parameter is invalid"}), mimetype="application/json", status=400)
        if limit>50:
            # number too big
            return Response(json.dumps({"message": "the limit parameter is invalid"}), mimetype="application/json", status=400)
        #posts = Post.query.limit(limit).all()
        posts = Post.query.filter(Post.user_id.in_(user_ids)).limit(limit).all()
        posts_json = [post.to_dict(user=self.current_user) for post in posts]
        return Response(json.dumps(posts_json), mimetype="application/json", status=200)

    def post(self): # HTTP POST
        # create a new post based on the data posted in the body 
        body = request.get_json()

        if not body.get('image_url'):
            return Response(json.dumps({"message": "'image_url' is required"}), mimetype="application/json", status=400)
        # insert whatever was posted into the database
        # (also some validation)
        new_post = Post(
            image_url=body.get('image_url'),
            user_id=self.current_user.id, # must be a valid user_id or will throw an error
            caption=body.get('caption'),
            alt_text=body.get('alt_text')
        )
        db.session.add(new_post)    # issues the insert statement
        db.session.commit()         # commits the change to the database 
        return Response(json.dumps(new_post.to_dict()), mimetype="application/json", status=201)

class PostDetailEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
        

    def patch(self, id):
        # update post based on the data posted in the body 
        body = request.get_json()
        print(body)
        # 1. retrieve existing post from the database
        post = Post.query.get(id)
        if not post:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        if post.user_id != self.current_user.id:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        
        # 2. set new values
        if body.get('image_url'):
            post.image_url = body.get('image_url')
        if body.get('caption'):
            post.caption = body.get('caption')
        if body.get('alt_text'):
            post.alt_text = body.get('alt_text')
        # 3. commit the post back to database (to persist changes)
        db.session.commit()
        return Response(json.dumps(post.to_dict()), mimetype="application/json", status=200)


    def delete(self, id):
        # delete post where "id"=id
        post = Post.query.get(id)
        if not post:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        if post.user_id != self.current_user.id:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        
        Post.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "Post id={0} was successfully deleted.".format(id)}), mimetype="application/json", status=200)


    def get(self, id):
        # need to query the database for the post where id=id
        post = Post.query.get(id)
        if not post:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        # users i'm connected to below
        user_ids = get_authorized_user_ids(self.current_user)
        if post.user_id not in user_ids:
            return Response(json.dumps({"message": "id={0} is invalid".format(id)}), mimetype="application/json", status=404)
        
        return Response(json.dumps(post.to_dict(user=self.current_user)), mimetype="application/json", status=200)

def initialize_routes(api):
    api.add_resource(
        PostListEndpoint, 
        '/api/posts', '/api/posts/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        PostDetailEndpoint, 
        '/api/posts/<int:id>', '/api/posts/<int:id>/',
        resource_class_kwargs={'current_user': api.app.current_user}
    )