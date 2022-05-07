from flask import Response, request
from flask_restful import Resource
from models import Following, User, db
import json
from views import get_authorized_user_ids

def get_path():
    return request.host_url + 'api/posts/'

class FollowingListEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def get(self):
        # return all of the "following" records that the current user is following
        followings = Following.query.filter_by(user_id = self.current_user.id).all()
        following_json = [following.to_dict_following() for following in followings]
        return Response(json.dumps(following_json), mimetype="application/json", status=200)


        

    def post(self):
        # create a new "following" record based on the data posted in the body 
        body = request.get_json()

        if not body.get('user_id'):
            return Response(json.dumps({"message": "'user_id' is required"}), mimetype="application/json", status=400)

        try:
            user = User.query.get(body.get('user_id'))
        except:
             return Response(json.dumps({"message": "user_id is invalid"}), mimetype="application/json", status=400)
        if not user:
            return Response(json.dumps({"message": "id={0} is invalid ".format(body.get('user_id'))}), mimetype="application/json", status=404)
        

        followings = Following.query.filter_by(user_id = self.current_user.id).all()
        for following in followings:
            if following.following_id == user.id:
                return Response(json.dumps({"message": "post_id is invalid"}), mimetype="application/json", status=400)

        new_following = Following( 
            user_id= self.current_user.id, # must be a valid user_id or will throw an error
            following_id = body.get('user_id'))
           
        db.session.add(new_following)  # issues the insert statement
        db.session.commit()      
        return Response(json.dumps(new_following.to_dict_following()), mimetype="application/json", status=201)
        
class FollowingDetailEndpoint(Resource):
    def __init__(self, current_user):
        self.current_user = current_user
    
    def delete(self, id):
        # delete "following" record where "id"=id
        print(id)
        following = Following.query.get(id)
        if not following:
            return Response(json.dumps({"message": "id={0} is invalid ".format(id)}), mimetype="application/json", status=404)

        if following.user_id != self.current_user.id:
            return Response(json.dumps({"message": "id={0} is invalid ".format(id)}), mimetype="application/json", status=404)


        Following.query.filter_by(id=id).delete()
        db.session.commit()
        return Response(json.dumps({"message": "following id = {0} was deleted "}), mimetype="application/json", status=200)

      

def initialize_routes(api):
    api.add_resource(
        FollowingListEndpoint, 
        '/api/following', 
        '/api/following/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
    api.add_resource(
        FollowingDetailEndpoint, 
        '/api/following/<int:id>', 
        '/api/following/<int:id>/', 
        resource_class_kwargs={'current_user': api.app.current_user}
    )
