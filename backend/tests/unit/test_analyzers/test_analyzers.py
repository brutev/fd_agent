import pytest
import tempfile
import os
from unittest.mock import Mock, patch, mock_open

from analyzers.flutter_analyzer import FlutterAnalyzer, FlutterWidget, BlocPattern
from analyzers.python_analyzer import PythonAnalyzer, APIEndpoint, PydanticModel, ServiceFunction

class TestFlutterAnalyzer:
    """Test Flutter analyzer with comprehensive scenarios"""
    
    @pytest.fixture
    def flutter_analyzer(self):
        return FlutterAnalyzer()
    
    def test_extract_stateless_widget(self, flutter_analyzer):
        """Test extraction of StatelessWidget"""
        dart_code = """
        import 'package:flutter/material.dart';
        
        class LoginPage extends StatelessWidget {
          @override
          Widget build(BuildContext context) {
            return Scaffold(
              body: Column(
                children: [
                  TextFormField(),
                  ElevatedButton(
                    onPressed: () => Navigator.pushNamed(context, '/home'),
                    child: Text('Login'),
                  ),
                ],
              ),
            );
          }
        }
        """
        
        widgets = flutter_analyzer._extract_widgets(dart_code, '/test/login_page.dart')
        
        assert len(widgets) == 1
        widget = widgets[0]
        assert widget.name == 'LoginPage'
        assert widget.type == 'StatelessWidget'
        assert widget.file_path == '/test/login_page.dart'
        assert widget.line_start == 3
    
    def test_extract_stateful_widget(self, flutter_analyzer):
        """Test extraction of StatefulWidget"""
        dart_code = """
        class TransactionPage extends StatefulWidget {
          @override
          _TransactionPageState createState() => _TransactionPageState();
        }
        
        class _TransactionPageState extends State<TransactionPage> {
          final _formKey = GlobalKey<FormState>();
          
          @override
          Widget build(BuildContext context) {
            return Form(
              key: _formKey,
              child: Column(
                children: [
                  TextFormField(
                    validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
                  ),
                ],
              ),
            );
          }
        }
        """
        
        widgets = flutter_analyzer._extract_widgets(dart_code, '/test/transaction_page.dart')
        
        assert len(widgets) == 1
        widget = widgets[0]
        assert widget.name == 'TransactionPage'
        assert widget.type == 'StatefulWidget'
    
    def test_extract_bloc_pattern(self, flutter_analyzer):
        """Test extraction of BLoC pattern"""
        dart_code = """
        import 'package:flutter_bloc/flutter_bloc.dart';
        
        class AuthBloc extends Bloc<AuthEvent, AuthState> {
          AuthBloc() : super(AuthInitial());
          
          @override
          Stream<AuthState> mapEventToState(AuthEvent event) async* {
            if (event is LoginEvent) {
              yield AuthLoading();
              // Login logic
              yield AuthSuccess();
            }
          }
        }
        
        abstract class AuthEvent {}
        class LoginEvent extends AuthEvent {}
        class LogoutEvent extends AuthEvent {}
        
        abstract class AuthState {}
        class AuthInitial extends AuthState {}
        class AuthLoading extends AuthState {}
        class AuthSuccess extends AuthState {}
        """
        
        blocs = flutter_analyzer._extract_bloc_patterns(dart_code, '/test/auth_bloc.dart')
        
        assert len(blocs) == 1
        bloc = blocs[0]
        assert bloc.name == 'AuthBloc'
        assert bloc.type == 'Bloc'
        assert 'LoginEvent' in bloc.events
        assert 'LogoutEvent' in bloc.events
        assert 'AuthInitial' in bloc.states
        assert 'AuthLoading' in bloc.states
        assert 'AuthSuccess' in bloc.states
    
    def test_extract_cubit_pattern(self, flutter_analyzer):
        """Test extraction of Cubit pattern"""
        dart_code = """
        import 'package:flutter_bloc/flutter_bloc.dart';
        
        class CounterCubit extends Cubit<CounterState> {
          CounterCubit() : super(CounterInitial());
          
          void increment() => emit(CounterValue(state.value + 1));
          void decrement() => emit(CounterValue(state.value - 1));
        }
        
        abstract class CounterState {
          final int value;
          CounterState(this.value);
        }
        
        class CounterInitial extends CounterState {
          CounterInitial() : super(0);
        }
        
        class CounterValue extends CounterState {
          CounterValue(int value) : super(value);
        }
        """
        
        blocs = flutter_analyzer._extract_bloc_patterns(dart_code, '/test/counter_cubit.dart')
        
        assert len(blocs) == 1
        cubit = blocs[0]
        assert cubit.name == 'CounterCubit'
        assert cubit.type == 'Cubit'
        assert len(cubit.events) == 0  # Cubits don't have events
        assert 'CounterInitial' in cubit.states
        assert 'CounterValue' in cubit.states
    
    def test_extract_api_calls(self, flutter_analyzer):
        """Test extraction of API calls"""
        dart_code = """
        import 'package:dio/dio.dart';
        import 'package:http/http.dart' as http;
        
        class ApiService {
          final Dio dio = Dio();
          
          Future<void> login() async {
            await dio.post('/api/v1/auth/login');
            await dio.get('/api/v1/user/profile');
          }
          
          Future<void> fetchData() async {
            await http.get(Uri.parse('/api/v1/data'));
            await http.post(Uri.parse('/api/v1/transactions'));
          }
        }
        """
        
        api_calls = flutter_analyzer._extract_api_calls(dart_code, '/test/api_service.dart')
        
        assert len(api_calls) == 4
        
        # Check Dio calls
        dio_calls = [call for call in api_calls if call['type'] == 'dio']
        assert len(dio_calls) == 2
        assert any(call['endpoint'] == '/api/v1/auth/login' and call['method'] == 'post' for call in dio_calls)
        assert any(call['endpoint'] == '/api/v1/user/profile' and call['method'] == 'get' for call in dio_calls)
        
        # Check HTTP calls
        http_calls = [call for call in api_calls if call['type'] == 'http']
        assert len(http_calls) == 2
        assert any(call['endpoint'] == '/api/v1/data' and call['method'] == 'get' for call in http_calls)
        assert any(call['endpoint'] == '/api/v1/transactions' and call['method'] == 'post' for call in http_calls)
    
    def test_extract_routes(self, flutter_analyzer):
        """Test extraction of navigation routes"""
        dart_code = """
        class NavigationHelper {
          static void goToHome(BuildContext context) {
            Navigator.pushNamed(context, '/home');
          }
          
          static void goToProfile(BuildContext context) {
            Navigator.pushNamed(context, '/profile');
          }
        }
        
        final routes = {
          '/home': (context) => HomePage(),
          '/profile': (context) => ProfilePage(),
          '/settings': (context) => SettingsPage(),
        };
        """
        
        routes = flutter_analyzer._extract_routes(dart_code, '/test/navigation.dart')
        
        push_routes = [route for route in routes if route['type'] == 'pushNamed']
        assert len(push_routes) == 2
        assert any(route['route'] == '/home' for route in push_routes)
        assert any(route['route'] == '/profile' for route in push_routes)
        
        route_definitions = [route for route in routes if route['type'] == 'route_definition']
        assert len(route_definitions) == 3
        assert any(route['route'] == '/home' and route['widget'] == 'HomePage' for route in route_definitions)
    
    def test_extract_form_validators(self, flutter_analyzer):
        """Test extraction of form validators"""
        dart_code = """
        class LoginForm extends StatefulWidget {
          @override
          Widget build(BuildContext context) {
            return Form(
              child: Column(
                children: [
                  TextFormField(
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Email is required';
                      }
                      if (!value!.contains('@')) {
                        return 'Invalid email format';
                      }
                      return null;
                    },
                  ),
                  TextFormField(
                    validator: (value) {
                      if (value?.isEmpty ?? true) {
                        return 'Password is required';
                      }
                      if (value!.length < 6) {
                        return 'Password must be at least 6 characters';
                      }
                      return null;
                    },
                  ),
                ],
              ),
            );
          }
        }
        """
        
        validators = flutter_analyzer._extract_form_validators(dart_code)
        
        assert len(validators) == 2
        
        # Check email validator
        email_validator = validators[0]
        assert 'Email is required' in email_validator['code']
        assert 'Invalid email format' in email_validator['code']
        
        # Check password validator
        password_validator = validators[1]
        assert 'Password is required' in password_validator['code']
        assert 'Password must be at least 6 characters' in password_validator['code']
    
    def test_analyze_pubspec(self, flutter_analyzer):
        """Test pubspec.yaml analysis"""
        pubspec_content = """
        name: fd_agent_mobile
        description: Financial Domain Agent Mobile App
        
        dependencies:
          flutter:
            sdk: flutter
          flutter_bloc: ^8.1.3
          dio: ^5.3.2
          shared_preferences: ^2.2.2
          local_auth: ^2.1.6
          
        dev_dependencies:
          flutter_test:
            sdk: flutter
          flutter_lints: ^2.0.0
          mockito: ^5.4.2
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(pubspec_content)
            f.flush()
            
            dependencies = flutter_analyzer._analyze_pubspec(f.name)
            
            assert 'flutter_bloc' in dependencies['dependencies']
            assert 'dio' in dependencies['dependencies']
            assert 'shared_preferences' in dependencies['dependencies']
            assert 'local_auth' in dependencies['dependencies']
            
            assert 'flutter_lints' in dependencies['dev_dependencies']
            assert 'mockito' in dependencies['dev_dependencies']
            
            os.unlink(f.name)
    
    def test_widget_dependencies_extraction(self, flutter_analyzer):
        """Test widget dependencies extraction"""
        dart_code = """
        class PaymentWidget extends StatelessWidget {
          @override
          Widget build(BuildContext context) {
            return BlocBuilder<PaymentBloc, PaymentState>(
              builder: (context, state) {
                return Provider.of<PaymentService>(context).when(
                  data: (service) => CustomButton(
                    onPressed: () => ApiClient.makePayment(),
                    child: Text('Pay'),
                  ),
                  loading: () => CircularProgressIndicator(),
                  error: (error) => ErrorWidget(error),
                );
              },
            );
          }
        }
        """
        
        widgets = flutter_analyzer._extract_widgets(dart_code, '/test/payment_widget.dart')
        widget = widgets[0]
        
        expected_deps = ['BlocBuilder', 'Provider', 'CustomButton', 'ApiClient', 'Text', 'CircularProgressIndicator', 'ErrorWidget']
        for dep in expected_deps:
            assert dep in widget.dependencies

class TestPythonAnalyzer:
    """Test Python analyzer with comprehensive scenarios"""
    
    @pytest.fixture
    def python_analyzer(self):
        return PythonAnalyzer()
    
    def test_extract_fastapi_endpoints(self, python_analyzer):
        """Test extraction of FastAPI endpoints"""
        python_code = """
        from fastapi import APIRouter, Depends
        from pydantic import BaseModel
        
        router = APIRouter()
        
        @router.get("/users/{user_id}")
        async def get_user(user_id: int, db: Session = Depends(get_db)):
            return {"user_id": user_id}
        
        @router.post("/users")
        async def create_user(user: UserCreate, db: Session = Depends(get_db)):
            return {"message": "User created"}
        
        @router.put("/users/{user_id}")
        async def update_user(user_id: int, user: UserUpdate):
            return {"message": "User updated"}
        
        @router.delete("/users/{user_id}")
        async def delete_user(user_id: int):
            return {"message": "User deleted"}
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            result = python_analyzer.analyze_python_file(f.name)
            endpoints = result.get('endpoints', [])
            
            assert len(endpoints) == 4
            
            # Check GET endpoint
            get_endpoint = next((ep for ep in endpoints if ep.method == 'GET'), None)
            assert get_endpoint is not None
            assert get_endpoint.name == 'get_user'
            assert get_endpoint.path == '/users/{user_id}'
            
            # Check POST endpoint
            post_endpoint = next((ep for ep in endpoints if ep.method == 'POST'), None)
            assert post_endpoint is not None
            assert post_endpoint.name == 'create_user'
            assert post_endpoint.path == '/users'
            
            os.unlink(f.name)
    
    def test_extract_pydantic_models(self, python_analyzer):
        """Test extraction of Pydantic models"""
        python_code = """
        from pydantic import BaseModel, validator
        from typing import Optional
        from datetime import datetime
        
        class UserBase(BaseModel):
            email: str
            full_name: str
            is_active: bool = True
            
            @validator('email')
            def validate_email(cls, v):
                if '@' not in v:
                    raise ValueError('Invalid email')
                return v
        
        class UserCreate(UserBase):
            password: str
            
            @validator('password')
            def validate_password(cls, v):
                if len(v) < 8:
                    raise ValueError('Password too short')
                return v
        
        class UserResponse(UserBase):
            id: int
            created_at: datetime
            
            class Config:
                orm_mode = True
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            result = python_analyzer.analyze_python_file(f.name)
            models = result.get('models', [])
            
            assert len(models) == 3
            
            # Check UserBase model
            user_base = next((m for m in models if m.name == 'UserBase'), None)
            assert user_base is not None
            assert len(user_base.fields) == 3
            assert any(field['name'] == 'email' for field in user_base.fields)
            assert any(field['name'] == 'full_name' for field in user_base.fields)
            assert any(field['name'] == 'is_active' for field in user_base.fields)
            assert 'validate_email' in user_base.validators
            
            # Check UserCreate model
            user_create = next((m for m in models if m.name == 'UserCreate'), None)
            assert user_create is not None
            assert 'UserBase' in user_create.base_classes
            assert 'validate_password' in user_create.validators
            
            os.unlink(f.name)
    
    def test_extract_service_functions(self, python_analyzer):
        """Test extraction of service functions"""
        python_code = """
        from sqlalchemy.orm import Session
        import requests
        
        def create_user(db: Session, user_data: dict) -> dict:
            # Database operations
            user = User(**user_data)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        
        def send_notification(user_id: int, message: str) -> bool:
            # External API call
            response = requests.post('/api/notifications', json={
                'user_id': user_id,
                'message': message
            })
            return response.status_code == 200
        
        def calculate_interest(principal: float, rate: float, time: int) -> float:
            return principal * rate * time / 100
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            result = python_analyzer.analyze_python_file(f.name)
            services = result.get('services', [])
            
            assert len(services) == 3
            
            # Check create_user service
            create_user_service = next((s for s in services if s.name == 'create_user'), None)
            assert create_user_service is not None
            assert 'add' in create_user_service.database_operations
            assert 'commit' in create_user_service.database_operations
            
            # Check send_notification service
            notification_service = next((s for s in services if s.name == 'send_notification'), None)
            assert notification_service is not None
            assert 'post' in notification_service.external_calls
            
            os.unlink(f.name)
    
    def test_extract_sqlalchemy_models(self, python_analyzer):
        """Test extraction of SQLAlchemy models"""
        python_code = """
        from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship
        
        Base = declarative_base()
        
        class User(Base):
            __tablename__ = 'users'
            
            id = Column(Integer, primary_key=True, index=True)
            email = Column(String, unique=True, index=True, nullable=False)
            full_name = Column(String, nullable=False)
            is_active = Column(Boolean, default=True)
            created_at = Column(DateTime)
            
            accounts = relationship("Account", back_populates="user")
        
        class Account(Base):
            __tablename__ = 'accounts'
            
            id = Column(Integer, primary_key=True)
            account_number = Column(String, unique=True, nullable=False)
            balance = Column(Integer, default=0)
            user_id = Column(Integer, ForeignKey('users.id'))
            
            user = relationship("User", back_populates="accounts")
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            result = python_analyzer.analyze_python_file(f.name)
            db_models = result.get('database_models', [])
            
            assert len(db_models) == 2
            
            # Check User model
            user_model = next((m for m in db_models if m['name'] == 'User'), None)
            assert user_model is not None
            assert user_model['table_name'] == 'users'
            assert len(user_model['columns']) == 5
            assert any(col['name'] == 'email' for col in user_model['columns'])
            assert any(rel['name'] == 'accounts' for rel in user_model['relationships'])
            
            # Check Account model
            account_model = next((m for m in db_models if m['name'] == 'Account'), None)
            assert account_model is not None
            assert account_model['table_name'] == 'accounts'
            assert any(col['name'] == 'user_id' for col in account_model['columns'])
            
            os.unlink(f.name)
    
    def test_extract_validators(self, python_analyzer):
        """Test extraction of validator functions"""
        python_code = """
        import re
        from pydantic import validator
        
        def validate_ifsc_code(ifsc: str) -> bool:
            pattern = r'^[A-Z]{4}0[A-Z0-9]{6}$'
            return bool(re.match(pattern, ifsc))
        
        def validate_pan_number(pan: str) -> bool:
            pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            return bool(re.match(pattern, pan))
        
        class UserModel(BaseModel):
            email: str
            
            @validator('email')
            def email_must_be_valid(cls, v):
                if '@' not in v:
                    raise ValueError('Invalid email')
                return v
        
        def check_transaction_limits(amount: float, transaction_type: str) -> bool:
            limits = {'NEFT': 1000000, 'UPI': 100000}
            return amount <= limits.get(transaction_type, 0)
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            result = python_analyzer.analyze_python_file(f.name)
            validators = result.get('validators', [])
            
            assert len(validators) >= 3
            
            validator_names = [v['name'] for v in validators]
            assert 'validate_ifsc_code' in validator_names
            assert 'validate_pan_number' in validator_names
            assert 'email_must_be_valid' in validator_names
            
            os.unlink(f.name)
    
    def test_analyze_requirements(self, python_analyzer):
        """Test requirements.txt analysis"""
        requirements_content = """
        fastapi==0.104.1
        uvicorn[standard]==0.24.0
        pydantic==2.5.0
        sqlalchemy==2.0.23
        # Development dependencies
        pytest==7.4.3
        pytest-cov==4.1.0
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(requirements_content)
            f.flush()
            
            dependencies = python_analyzer._analyze_requirements(f.name)
            
            assert 'fastapi' in dependencies['packages']
            assert 'uvicorn' in dependencies['packages']
            assert 'pydantic' in dependencies['packages']
            assert 'sqlalchemy' in dependencies['packages']
            assert 'pytest' in dependencies['packages']
            assert 'pytest-cov' in dependencies['packages']
            
            os.unlink(f.name)
    
    def test_extract_middleware(self, python_analyzer):
        """Test extraction of middleware"""
        python_code = """
        from fastapi import Request, Response
        from starlette.middleware.base import BaseHTTPMiddleware
        
        class AuthMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Authentication logic
                response = await call_next(request)
                return response
        
        class RateLimitMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next):
                # Rate limiting logic
                response = await call_next(request)
                return response
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            result = python_analyzer.analyze_python_file(f.name)
            middleware = result.get('middleware', [])
            
            assert len(middleware) == 2
            
            middleware_names = [m['name'] for m in middleware]
            assert 'AuthMiddleware' in middleware_names
            assert 'RateLimitMiddleware' in middleware_names
            
            # Check methods
            auth_middleware = next((m for m in middleware if m['name'] == 'AuthMiddleware'), None)
            assert 'dispatch' in auth_middleware['methods']
            
            os.unlink(f.name)

# Integration tests for analyzers
class TestAnalyzerIntegration:
    """Integration tests for analyzer interactions"""
    
    def test_flutter_python_api_mapping(self):
        """Test mapping between Flutter API calls and Python endpoints"""
        flutter_analyzer = FlutterAnalyzer()
        python_analyzer = PythonAnalyzer()
        
        # Flutter code with API call
        flutter_code = """
        class UserService {
          Future<User> getUser(int userId) async {
            final response = await dio.get('/api/v1/users/$userId');
            return User.fromJson(response.data);
          }
        }
        """
        
        # Python code with matching endpoint
        python_code = """
        from fastapi import APIRouter
        
        router = APIRouter()
        
        @router.get("/api/v1/users/{user_id}")
        async def get_user(user_id: int):
            return {"id": user_id, "name": "Test User"}
        """
        
        # Analyze Flutter code
        flutter_api_calls = flutter_analyzer._extract_api_calls(flutter_code, '/flutter/user_service.dart')
        
        # Analyze Python code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            python_result = python_analyzer.analyze_python_file(f.name)
            python_endpoints = python_result.get('endpoints', [])
            
            os.unlink(f.name)
        
        # Verify mapping potential
        assert len(flutter_api_calls) == 1
        assert len(python_endpoints) == 1
        
        flutter_call = flutter_api_calls[0]
        python_endpoint = python_endpoints[0]
        
        # Check if they can be mapped
        assert flutter_call['method'].upper() == python_endpoint.method
        assert '/api/v1/users' in flutter_call['endpoint']
        assert '/api/v1/users' in python_endpoint.path
    
    def test_validation_pattern_matching(self):
        """Test matching validation patterns between Flutter and Python"""
        flutter_analyzer = FlutterAnalyzer()
        python_analyzer = PythonAnalyzer()
        
        # Flutter validation code
        flutter_code = """
        TextFormField(
          validator: (value) {
            if (value?.isEmpty ?? true) {
              return 'Email is required';
            }
            if (!value!.contains('@')) {
              return 'Invalid email format';
            }
            return null;
          },
        )
        """
        
        # Python validation code
        python_code = """
        def validate_email(email: str) -> bool:
            if not email:
                return False
            if '@' not in email:
                return False
            return True
        """
        
        # Extract validations
        flutter_validators = flutter_analyzer._extract_form_validators(flutter_code)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            f.flush()
            
            python_result = python_analyzer.analyze_python_file(f.name)
            python_validators = python_result.get('validators', [])
            
            os.unlink(f.name)
        
        # Verify similar validation logic
        assert len(flutter_validators) == 1
        assert len(python_validators) == 1
        
        flutter_validator = flutter_validators[0]
        python_validator = python_validators[0]
        
        # Both should contain email validation logic
        assert 'email' in flutter_validator['code'].lower()
        assert '@' in flutter_validator['code']
        assert 'email' in python_validator['name'].lower()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=analyzers', '--cov-report=html'])