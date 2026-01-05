import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'core/di/injection_container.dart';
import 'core/theme/app_theme.dart';
import 'core/routes/app_routes.dart';
import 'core/routes/route_generator.dart';
import 'features/auth/presentation/bloc/auth_bloc.dart';
import 'features/accounts/presentation/bloc/account_bloc.dart';
import 'features/transactions/presentation/bloc/transaction_bloc.dart';
import 'features/kyc/presentation/bloc/kyc_bloc.dart';

class FDAgentApp extends StatelessWidget {
  const FDAgentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (context) => sl<AuthBloc>()..add(CheckAuthStatusEvent()),
        ),
        BlocProvider<AccountBloc>(
          create: (context) => sl<AccountBloc>(),
        ),
        BlocProvider<TransactionBloc>(
          create: (context) => sl<TransactionBloc>(),
        ),
        BlocProvider<KycBloc>(
          create: (context) => sl<KycBloc>(),
        ),
      ],
      child: MaterialApp(
        title: 'FD Agent - Banking App',
        debugShowCheckedModeBanner: false,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: ThemeMode.system,
        initialRoute: AppRoutes.splash,
        onGenerateRoute: RouteGenerator.generateRoute,
        builder: (context, child) {
          return MediaQuery(
            data: MediaQuery.of(context).copyWith(
              textScaleFactor: MediaQuery.of(context).textScaleFactor.clamp(0.8, 1.2),
            ),
            child: child!,
          );
        },
      ),
    );
  }
}