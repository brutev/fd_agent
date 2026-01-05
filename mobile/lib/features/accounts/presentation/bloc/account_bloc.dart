import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

// Events
abstract class AccountEvent extends Equatable {
  const AccountEvent();

  @override
  List<Object?> get props => [];
}

class LoadAccountsEvent extends AccountEvent {}

class LoadAccountDetailsEvent extends AccountEvent {
  final String accountId;

  const LoadAccountDetailsEvent({required this.accountId});

  @override
  List<Object?> get props => [accountId];
}

class CreateAccountEvent extends AccountEvent {
  final String accountType;
  final double initialDeposit;

  const CreateAccountEvent({
    required this.accountType,
    required this.initialDeposit,
  });

  @override
  List<Object?> get props => [accountType, initialDeposit];
}

// States
abstract class AccountState extends Equatable {
  const AccountState();

  @override
  List<Object?> get props => [];
}

class AccountInitial extends AccountState {}

class AccountLoading extends AccountState {}

class AccountsLoaded extends AccountState {
  final List<Account> accounts;

  const AccountsLoaded({required this.accounts});

  @override
  List<Object?> get props => [accounts];
}

class AccountDetailsLoaded extends AccountState {
  final Account account;

  const AccountDetailsLoaded({required this.account});

  @override
  List<Object?> get props => [account];
}

class AccountCreated extends AccountState {
  final Account account;

  const AccountCreated({required this.account});

  @override
  List<Object?> get props => [account];
}

class AccountError extends AccountState {
  final String message;

  const AccountError({required this.message});

  @override
  List<Object?> get props => [message];
}

// Model
class Account extends Equatable {
  final String id;
  final String accountNumber;
  final String accountType;
  final double balance;
  final String currency;
  final DateTime createdAt;

  const Account({
    required this.id,
    required this.accountNumber,
    required this.accountType,
    required this.balance,
    required this.currency,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [
        id,
        accountNumber,
        accountType,
        balance,
        currency,
        createdAt,
      ];
}

// Bloc
class AccountBloc extends Bloc<AccountEvent, AccountState> {
  AccountBloc() : super(AccountInitial()) {
    on<LoadAccountsEvent>(_onLoadAccounts);
    on<LoadAccountDetailsEvent>(_onLoadAccountDetails);
    on<CreateAccountEvent>(_onCreateAccount);
  }

  Future<void> _onLoadAccounts(
    LoadAccountsEvent event,
    Emitter<AccountState> emit,
  ) async {
    emit(AccountLoading());
    
    try {
      // TODO: Implement actual account loading logic
      await Future.delayed(const Duration(seconds: 1));
      
      // Mock accounts data
      final accounts = [
        Account(
          id: '1',
          accountNumber: '1234567890',
          accountType: 'Savings',
          balance: 50000.0,
          currency: 'INR',
          createdAt: DateTime.now().subtract(const Duration(days: 365)),
        ),
        Account(
          id: '2',
          accountNumber: '0987654321',
          accountType: 'Current',
          balance: 100000.0,
          currency: 'INR',
          createdAt: DateTime.now().subtract(const Duration(days: 180)),
        ),
      ];
      
      emit(AccountsLoaded(accounts: accounts));
    } catch (e) {
      emit(AccountError(message: e.toString()));
    }
  }

  Future<void> _onLoadAccountDetails(
    LoadAccountDetailsEvent event,
    Emitter<AccountState> emit,
  ) async {
    emit(AccountLoading());
    
    try {
      // TODO: Implement actual account details loading logic
      await Future.delayed(const Duration(milliseconds: 500));
      
      // Mock account details
      final account = Account(
        id: event.accountId,
        accountNumber: '1234567890',
        accountType: 'Savings',
        balance: 50000.0,
        currency: 'INR',
        createdAt: DateTime.now().subtract(const Duration(days: 365)),
      );
      
      emit(AccountDetailsLoaded(account: account));
    } catch (e) {
      emit(AccountError(message: e.toString()));
    }
  }

  Future<void> _onCreateAccount(
    CreateAccountEvent event,
    Emitter<AccountState> emit,
  ) async {
    emit(AccountLoading());
    
    try {
      // TODO: Implement actual account creation logic
      await Future.delayed(const Duration(seconds: 1));
      
      // Mock account creation
      final account = Account(
        id: '3',
        accountNumber: '1122334455',
        accountType: event.accountType,
        balance: event.initialDeposit,
        currency: 'INR',
        createdAt: DateTime.now(),
      );
      
      emit(AccountCreated(account: account));
    } catch (e) {
      emit(AccountError(message: e.toString()));
    }
  }
}
