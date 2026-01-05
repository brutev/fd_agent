import 'package:flutter/material.dart';

import 'app_routes.dart';

class RouteGenerator {
  static Route<dynamic> generateRoute(RouteSettings settings) {
    final args = settings.arguments;

    switch (settings.name) {
      case AppRoutes.splash:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          ),
        );

      case AppRoutes.onboarding:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Onboarding Screen'),
            ),
          ),
        );

      case AppRoutes.login:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Login Screen'),
            ),
          ),
        );

      case AppRoutes.register:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Register Screen'),
            ),
          ),
        );

      case AppRoutes.home:
      case AppRoutes.dashboard:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Dashboard Screen'),
            ),
          ),
        );

      case AppRoutes.accounts:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Accounts Screen'),
            ),
          ),
        );

      case AppRoutes.transactions:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Transactions Screen'),
            ),
          ),
        );

      case AppRoutes.kyc:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('KYC Screen'),
            ),
          ),
        );

      case AppRoutes.loans:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Loans Screen'),
            ),
          ),
        );

      case AppRoutes.profile:
        return MaterialPageRoute(
          builder: (_) => const Scaffold(
            body: Center(
              child: Text('Profile Screen'),
            ),
          ),
        );

      default:
        return _errorRoute(settings.name);
    }
  }

  static Route<dynamic> _errorRoute(String? routeName) {
    return MaterialPageRoute(
      builder: (_) => Scaffold(
        appBar: AppBar(
          title: const Text('Error'),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(
                Icons.error_outline,
                size: 64,
                color: Colors.red,
              ),
              const SizedBox(height: 16),
              Text(
                'Route not found',
                style: Theme.of(_).textTheme.headlineMedium,
              ),
              const SizedBox(height: 8),
              Text(
                routeName ?? 'Unknown route',
                style: Theme.of(_).textTheme.bodyMedium,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
