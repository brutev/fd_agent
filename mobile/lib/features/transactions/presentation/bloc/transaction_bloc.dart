import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../domain/entities/beneficiary.dart';

// Events
abstract class TransactionEvent extends Equatable {
  const TransactionEvent();

  @override
  List<Object?> get props => [];
}

class LoadTransactionsEvent extends TransactionEvent {
  final String? accountId;

  const LoadTransactionsEvent({this.accountId});

  @override
  List<Object?> get props => [accountId];
}

class LoadTransactionDetailsEvent extends TransactionEvent {
  final String transactionId;

  const LoadTransactionDetailsEvent({required this.transactionId});

  @override
  List<Object?> get props => [transactionId];
}

class CreateTransactionEvent extends TransactionEvent {
  final String fromAccountId;
  final String toAccountId;
  final double amount;
  final String transactionType;
  final String? description;

  const CreateTransactionEvent({
    required this.fromAccountId,
    required this.toAccountId,
    required this.amount,
    required this.transactionType,
    this.description,
  });

  @override
  List<Object?> get props => [
        fromAccountId,
        toAccountId,
        amount,
        transactionType,
        description,
      ];
}

class ValidateTransactionEvent extends TransactionEvent {
  final String ifscCode;
  final String accountNumber;
  final double amount;
  final String? remarks;

  const ValidateTransactionEvent({
    required this.ifscCode,
    required this.accountNumber,
    required this.amount,
    this.remarks,
  });

  @override
  List<Object?> get props => [ifscCode, accountNumber, amount, remarks];
}

class ConfirmTransactionEvent extends TransactionEvent {}

class VerifyOTPEvent extends TransactionEvent {
  final String otp;

  const VerifyOTPEvent({required this.otp});

  @override
  List<Object?> get props => [otp];
}

class ResendOTPEvent extends TransactionEvent {}

class VerifyMPINEvent extends TransactionEvent {
  final String mpin;

  const VerifyMPINEvent({required this.mpin});

  @override
  List<Object?> get props => [mpin];
}

class RetryTransactionEvent extends TransactionEvent {}

class ResetTransactionEvent extends TransactionEvent {}

// States
abstract class TransactionState extends Equatable {
  const TransactionState();

  @override
  List<Object?> get props => [];
}

class TransactionInitial extends TransactionState {}

class TransactionLoading extends TransactionState {}

class TransactionsLoaded extends TransactionState {
  final List<Transaction> transactions;

  const TransactionsLoaded({required this.transactions});

  @override
  List<Object?> get props => [transactions];
}

class TransactionDetailsLoaded extends TransactionState {
  final Transaction transaction;

  const TransactionDetailsLoaded({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

class TransactionCreated extends TransactionState {
  final Transaction transaction;

  const TransactionCreated({required this.transaction});

  @override
  List<Object?> get props => [transaction];
}

class TransactionError extends TransactionState {
  final String message;

  const TransactionError({required this.message});

  @override
  List<Object?> get props => [message];
}

class TransactionValidated extends TransactionState {}

class TransactionOTPRequired extends TransactionState {}

class TransactionMPINRequired extends TransactionState {}

class TransactionSuccess extends TransactionState {
  final String transactionId;
  final double amount;
  final String beneficiaryName;
  final DateTime timestamp;

  const TransactionSuccess({
    required this.transactionId,
    required this.amount,
    required this.beneficiaryName,
    required this.timestamp,
  });

  @override
  List<Object?> get props => [transactionId, amount, beneficiaryName, timestamp];
}

class TransactionFailure extends TransactionState {
  final String error;

  const TransactionFailure({required this.error});

  @override
  List<Object?> get props => [error];
}

class BeneficiariesLoaded extends TransactionState {
  final List<Beneficiary> beneficiaries;

  const BeneficiariesLoaded({required this.beneficiaries});

  @override
  List<Object?> get props => [beneficiaries];
}

// Model
class Transaction extends Equatable {
  final String id;
  final String fromAccountId;
  final String toAccountId;
  final double amount;
  final String currency;
  final String transactionType;
  final String status;
  final String? description;
  final DateTime createdAt;

  const Transaction({
    required this.id,
    required this.fromAccountId,
    required this.toAccountId,
    required this.amount,
    required this.currency,
    required this.transactionType,
    required this.status,
    this.description,
    required this.createdAt,
  });

  @override
  List<Object?> get props => [
        id,
        fromAccountId,
        toAccountId,
        amount,
        currency,
        transactionType,
        status,
        description,
        createdAt,
      ];
}

// Bloc
class TransactionBloc extends Bloc<TransactionEvent, TransactionState> {
  TransactionBloc() : super(TransactionInitial()) {
    on<LoadTransactionsEvent>(_onLoadTransactions);
    on<LoadTransactionDetailsEvent>(_onLoadTransactionDetails);
    on<CreateTransactionEvent>(_onCreateTransaction);
  }

  Future<void> _onLoadTransactions(
    LoadTransactionsEvent event,
    Emitter<TransactionState> emit,
  ) async {
    emit(TransactionLoading());
    
    try {
      // TODO: Implement actual transaction loading logic
      await Future.delayed(const Duration(seconds: 1));
      
      // Mock transactions data
      final transactions = [
        Transaction(
          id: '1',
          fromAccountId: '1',
          toAccountId: '2',
          amount: 5000.0,
          currency: 'INR',
          transactionType: 'NEFT',
          status: 'completed',
          description: 'Payment for services',
          createdAt: DateTime.now().subtract(const Duration(days: 1)),
        ),
        Transaction(
          id: '2',
          fromAccountId: '1',
          toAccountId: '3',
          amount: 10000.0,
          currency: 'INR',
          transactionType: 'IMPS',
          status: 'completed',
          description: 'Transfer to savings',
          createdAt: DateTime.now().subtract(const Duration(days: 5)),
        ),
        Transaction(
          id: '3',
          fromAccountId: '2',
          toAccountId: '1',
          amount: 2500.0,
          currency: 'INR',
          transactionType: 'UPI',
          status: 'pending',
          description: 'Refund',
          createdAt: DateTime.now().subtract(const Duration(hours: 2)),
        ),
      ];
      
      emit(TransactionsLoaded(transactions: transactions));
    } catch (e) {
      emit(TransactionError(message: e.toString()));
    }
  }

  Future<void> _onLoadTransactionDetails(
    LoadTransactionDetailsEvent event,
    Emitter<TransactionState> emit,
  ) async {
    emit(TransactionLoading());
    
    try {
      // TODO: Implement actual transaction details loading logic
      await Future.delayed(const Duration(milliseconds: 500));
      
      // Mock transaction details
      final transaction = Transaction(
        id: event.transactionId,
        fromAccountId: '1',
        toAccountId: '2',
        amount: 5000.0,
        currency: 'INR',
        transactionType: 'NEFT',
        status: 'completed',
        description: 'Payment for services',
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
      );
      
      emit(TransactionDetailsLoaded(transaction: transaction));
    } catch (e) {
      emit(TransactionError(message: e.toString()));
    }
  }

  Future<void> _onCreateTransaction(
    CreateTransactionEvent event,
    Emitter<TransactionState> emit,
  ) async {
    emit(TransactionLoading());
    
    try {
      // TODO: Implement actual transaction creation logic
      await Future.delayed(const Duration(seconds: 2));
      
      // Mock transaction creation
      final transaction = Transaction(
        id: '4',
        fromAccountId: event.fromAccountId,
        toAccountId: event.toAccountId,
        amount: event.amount,
        currency: 'INR',
        transactionType: event.transactionType,
        status: 'completed',
        description: event.description,
        createdAt: DateTime.now(),
      );
      
      emit(TransactionCreated(transaction: transaction));
    } catch (e) {
      emit(TransactionError(message: e.toString()));
    }
  }
}
