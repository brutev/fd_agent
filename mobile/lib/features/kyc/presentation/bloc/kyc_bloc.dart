import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

// Events
abstract class KycEvent extends Equatable {
  const KycEvent();

  @override
  List<Object?> get props => [];
}

class LoadKycStatusEvent extends KycEvent {}

class SubmitAadhaarEvent extends KycEvent {
  final String aadhaarNumber;

  const SubmitAadhaarEvent({required this.aadhaarNumber});

  @override
  List<Object?> get props => [aadhaarNumber];
}

class SubmitPanEvent extends KycEvent {
  final String panNumber;

  const SubmitPanEvent({required this.panNumber});

  @override
  List<Object?> get props => [panNumber];
}

class VerifyKycEvent extends KycEvent {
  final String otp;

  const VerifyKycEvent({required this.otp});

  @override
  List<Object?> get props => [otp];
}

// States
abstract class KycState extends Equatable {
  const KycState();

  @override
  List<Object?> get props => [];
}

class KycInitial extends KycState {}

class KycLoading extends KycState {}

class KycStatusLoaded extends KycState {
  final KycStatus status;

  const KycStatusLoaded({required this.status});

  @override
  List<Object?> get props => [status];
}

class KycAadhaarSubmitted extends KycState {
  final String message;

  const KycAadhaarSubmitted({required this.message});

  @override
  List<Object?> get props => [message];
}

class KycPanSubmitted extends KycState {
  final String message;

  const KycPanSubmitted({required this.message});

  @override
  List<Object?> get props => [message];
}

class KycVerified extends KycState {
  final String message;

  const KycVerified({required this.message});

  @override
  List<Object?> get props => [message];
}

class KycError extends KycState {
  final String message;

  const KycError({required this.message});

  @override
  List<Object?> get props => [message];
}

// Model
class KycStatus extends Equatable {
  final String userId;
  final bool isAadhaarVerified;
  final bool isPanVerified;
  final bool isKycComplete;
  final String? aadhaarNumber;
  final String? panNumber;
  final DateTime? verifiedAt;

  const KycStatus({
    required this.userId,
    required this.isAadhaarVerified,
    required this.isPanVerified,
    required this.isKycComplete,
    this.aadhaarNumber,
    this.panNumber,
    this.verifiedAt,
  });

  @override
  List<Object?> get props => [
        userId,
        isAadhaarVerified,
        isPanVerified,
        isKycComplete,
        aadhaarNumber,
        panNumber,
        verifiedAt,
      ];
}

// Bloc
class KycBloc extends Bloc<KycEvent, KycState> {
  KycBloc() : super(KycInitial()) {
    on<LoadKycStatusEvent>(_onLoadKycStatus);
    on<SubmitAadhaarEvent>(_onSubmitAadhaar);
    on<SubmitPanEvent>(_onSubmitPan);
    on<VerifyKycEvent>(_onVerifyKyc);
  }

  Future<void> _onLoadKycStatus(
    LoadKycStatusEvent event,
    Emitter<KycState> emit,
  ) async {
    emit(KycLoading());
    
    try {
      // TODO: Implement actual KYC status loading logic
      await Future.delayed(const Duration(seconds: 1));
      
      // Mock KYC status
      final status = KycStatus(
        userId: '123',
        isAadhaarVerified: false,
        isPanVerified: false,
        isKycComplete: false,
        aadhaarNumber: null,
        panNumber: null,
        verifiedAt: null,
      );
      
      emit(KycStatusLoaded(status: status));
    } catch (e) {
      emit(KycError(message: e.toString()));
    }
  }

  Future<void> _onSubmitAadhaar(
    SubmitAadhaarEvent event,
    Emitter<KycState> emit,
  ) async {
    emit(KycLoading());
    
    try {
      // TODO: Implement actual Aadhaar submission logic
      await Future.delayed(const Duration(seconds: 1));
      
      emit(const KycAadhaarSubmitted(
        message: 'Aadhaar submitted successfully. Please verify with OTP.',
      ));
    } catch (e) {
      emit(KycError(message: e.toString()));
    }
  }

  Future<void> _onSubmitPan(
    SubmitPanEvent event,
    Emitter<KycState> emit,
  ) async {
    emit(KycLoading());
    
    try {
      // TODO: Implement actual PAN submission logic
      await Future.delayed(const Duration(seconds: 1));
      
      emit(const KycPanSubmitted(
        message: 'PAN submitted successfully. Verification in progress.',
      ));
    } catch (e) {
      emit(KycError(message: e.toString()));
    }
  }

  Future<void> _onVerifyKyc(
    VerifyKycEvent event,
    Emitter<KycState> emit,
  ) async {
    emit(KycLoading());
    
    try {
      // TODO: Implement actual KYC verification logic
      await Future.delayed(const Duration(seconds: 2));
      
      emit(const KycVerified(
        message: 'KYC verified successfully!',
      ));
    } catch (e) {
      emit(KycError(message: e.toString()));
    }
  }
}
