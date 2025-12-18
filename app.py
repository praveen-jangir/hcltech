from flask import Flask, render_template, request, Blueprint
from flask_restx import Api, Resource, fields

app = Flask(__name__)
blueprint = Blueprint('api', __name__, url_prefix='/api')
api = Api(blueprint, version='1.0', title='Excellent Mirror API',
          description='A simple API for HCL Tech Hackathon Project',
          doc='/docs')

app.register_blueprint(blueprint)

ns = api.namespace('test', description='Test operations')

test_model = api.model('Test', {
    'key': fields.String(required=True, description='A test key'),
    'value': fields.String(description='A test value')
})

@app.route('/')
def home():
    """Serves the 'Coming Soon' landing page."""
    return render_template('index.html')

@ns.route('/')
class TestResource(Resource):
    @ns.doc('get_test')
    def get(self):
        """Fetch a test message"""
        return {'status': 'active', 'message': 'Test API is working'}

    @ns.doc('create_test')
    @ns.expect(test_model)
    def post(self):
        """Send a test payload"""
        data = request.json
        return {'status': 'received', 'data': data, 'message': 'Payload received successfully'}

if __name__ == '__main__':
    app.run(debug=False, port=8000, host='0.0.0.0')
