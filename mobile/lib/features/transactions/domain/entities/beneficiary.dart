import 'package:equatable/equatable.dart';

class Beneficiary extends Equatable {
  final String id;
  final String name;
  final String accountNumber;
  final String ifscCode;
  final String bankName;

  const Beneficiary({
    required this.id,
    required this.name,
    required this.accountNumber,
    required this.ifscCode,
    required this.bankName,
  });

  @override
  List<Object?> get props => [id, name, accountNumber, ifscCode, bankName];
}
