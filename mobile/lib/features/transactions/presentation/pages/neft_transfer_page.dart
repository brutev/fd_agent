import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/transaction_bloc.dart';
import '../../../../shared/widgets/custom_button.dart';
import '../../../../shared/widgets/custom_text_field.dart';
import '../../domain/entities/beneficiary.dart';

class NEFTTransferPage extends StatefulWidget {
  const NEFTTransferPage({Key? key}) : super(key: key);

  @override
  State<NEFTTransferPage> createState() => _NEFTTransferPageState();
}

class _NEFTTransferPageState extends State<NEFTTransferPage> {
  final _formKey = GlobalKey<FormState>();
  final _ifscController = TextEditingController();
  final _accountController = TextEditingController();
  final _amountController = TextEditingController();
  final _remarksController = TextEditingController();
  
  Beneficiary? _selectedBeneficiary;
  String? _ifscError;
  String? _accountError;
  String? _amountError;
  String? _remarksError;

  @override
  void dispose() {
    _ifscController.dispose();
    _accountController.dispose();
    _amountController.dispose();
    _remarksController.dispose();
    super.dispose();
  }

  void _resetForm() {
    _formKey.currentState?.reset();
    _ifscController.clear();
    _accountController.clear();
    _amountController.clear();
    _remarksController.clear();
    setState(() {
      _selectedBeneficiary = null;
      _ifscError = null;
      _accountError = null;
      _amountError = null;
      _remarksError = null;
    });
  }

  String? _validateIFSC(String? value) {
    if (value == null || value.isEmpty) return null;
    final ifscRegex = RegExp(r'^[A-Z]{4}0[A-Z0-9]{6}$');
    if (!ifscRegex.hasMatch(value)) {
      return 'Invalid IFSC code format';
    }
    return null;
  }

  String? _validateAccount(String? value) {
    if (value == null || value.isEmpty) return null;
    if (value.length < 9 || value.length > 18) {
      return 'Account number must be 9-18 digits';
    }
    return null;
  }

  String? _validateAmount(String? value) {
    if (value == null || value.isEmpty) return null;
    final amount = double.tryParse(value);
    if (amount == null) return 'Invalid amount';
    if (amount < 1) {
      return 'Amount must be at least ₹1.00';
    }
    if (amount > 1000000) {
      return 'Amount cannot exceed ₹10,00,000.00';
    }
    return null;
  }

  String? _validateRemarks(String? value) {
    if (value == null || value.isEmpty) return null;
    if (value.length > 50) {
      return 'Remarks cannot exceed 50 characters';
    }
    if (RegExp(r'[@#\$%]').hasMatch(value)) {
      return 'Remarks contain invalid characters';
    }
    return null;
  }

  void _handleTransfer() {
    setState(() {
      _ifscError = _validateIFSC(_ifscController.text);
      _accountError = _validateAccount(_accountController.text);
      _amountError = _validateAmount(_amountController.text);
      _remarksError = _validateRemarks(_remarksController.text);
    });

    if (_ifscError == null && _accountError == null && _amountError == null && _remarksError == null) {
      context.read<TransactionBloc>().add(
        ValidateTransactionEvent(
          ifscCode: _ifscController.text,
          accountNumber: _accountController.text,
          amount: double.parse(_amountController.text),
          remarks: _remarksController.text,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NEFT Transfer'),
        leading: const BackButton(),
      ),
      body: BlocConsumer<TransactionBloc, TransactionState>(
        listener: (context, state) {
          if (state is TransactionSuccess) {
            _resetForm();
          }
        },
        builder: (context, state) {
          if (state is TransactionLoading) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Processing Transaction...'),
                ],
              ),
            );
          }

          if (state is TransactionOTPRequired) {
            return _buildOTPScreen();
          }

          if (state is TransactionMPINRequired) {
            return _buildMPINScreen();
          }

          if (state is TransactionSuccess) {
            return _buildSuccessScreen(state);
          }

          if (state is TransactionFailure) {
            return _buildErrorScreen(state);
          }

          if (state is TransactionValidated) {
            return _buildConfirmationScreen();
          }

          if (state is BeneficiariesLoaded) {
            return _buildTransferForm(context, state.beneficiaries, state);
          }

          return _buildTransferForm(context, [], state);
        },
      ),
    );
  }

  Widget _buildTransferForm(BuildContext context, List<Beneficiary> beneficiaries, TransactionState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text('NEFT Limits: ₹1 - ₹10,00,000'),
            const Text('Operating Hours: 8:00 AM - 7:00 PM'),
            const SizedBox(height: 24),
            
            DropdownButtonFormField<Beneficiary>(
              decoration: const InputDecoration(
                labelText: 'Select Beneficiary',
              ),
              value: _selectedBeneficiary,
              items: beneficiaries.map((b) => DropdownMenuItem(
                value: b,
                child: Text(b.name),
              )).toList(),
              onChanged: (beneficiary) {
                setState(() {
                  _selectedBeneficiary = beneficiary;
                  if (beneficiary != null) {
                    _ifscController.text = beneficiary.ifscCode;
                    _accountController.text = beneficiary.accountNumber;
                  }
                });
              },
            ),
            
            TextButton(
              onPressed: () {},
              child: const Text('Add New Beneficiary'),
            ),
            
            const SizedBox(height: 16),
            
            CustomTextField(
              controller: _ifscController,
              labelText: 'IFSC Code',
              errorText: _ifscError,
            ),
            
            const SizedBox(height: 16),
            
            CustomTextField(
              controller: _accountController,
              labelText: 'Account Number',
              errorText: _accountError,
              keyboardType: TextInputType.number,
            ),
            
            const SizedBox(height: 16),
            
            CustomTextField(
              controller: _amountController,
              labelText: 'Amount',
              errorText: _amountError,
              keyboardType: TextInputType.number,
            ),
            
            const SizedBox(height: 16),
            
            CustomTextField(
              controller: _remarksController,
              labelText: 'Remarks (Optional)',
              errorText: _remarksError,
              maxLength: 50,
            ),
            
            const SizedBox(height: 24),
            
            BlocBuilder<TransactionBloc, TransactionState>(
              builder: (builderContext, blocState) {
                return CustomButton(
                  onPressed: (blocState is TransactionLoading) ? null : _handleTransfer,
                  child: const Text('Transfer'),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildConfirmationScreen() {
    final amount = double.tryParse(_amountController.text) ?? 0;
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('Confirm Transfer', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 24),
          Text('₹${amount.toStringAsFixed(2)}', style: const TextStyle(fontSize: 32)),
          const SizedBox(height: 16),
          Text('IFSC: ${_ifscController.text}'),
          const SizedBox(height: 32),
          CustomButton(
            onPressed: () {
              context.read<TransactionBloc>().add(ConfirmTransactionEvent());
            },
            child: const Text('Confirm'),
          ),
        ],
      ),
    );
  }

  Widget _buildOTPScreen() {
    final otpController = TextEditingController();
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('Enter OTP', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          const Text('OTP sent to your registered mobile number'),
          const SizedBox(height: 24),
          TextField(
            controller: otpController,
            decoration: const InputDecoration(labelText: 'OTP'),
            keyboardType: TextInputType.number,
            maxLength: 6,
          ),
          const SizedBox(height: 16),
          CustomButton(
            onPressed: () {
              context.read<TransactionBloc>().add(VerifyOTPEvent(otp: otpController.text));
            },
            child: const Text('Verify OTP'),
          ),
          TextButton(
            onPressed: () {
              context.read<TransactionBloc>().add(ResendOTPEvent());
            },
            child: const Text('Resend OTP'),
          ),
        ],
      ),
    );
  }

  Widget _buildMPINScreen() {
    final mpinController = TextEditingController();
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('Enter MPIN', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          const Text('Enter your 4-digit MPIN'),
          const SizedBox(height: 24),
          TextField(
            controller: mpinController,
            decoration: const InputDecoration(labelText: 'MPIN'),
            keyboardType: TextInputType.number,
            maxLength: 4,
            obscureText: true,
          ),
          const SizedBox(height: 16),
          CustomButton(
            onPressed: () {
              context.read<TransactionBloc>().add(VerifyMPINEvent(mpin: mpinController.text));
            },
            child: const Text('Verify MPIN'),
          ),
        ],
      ),
    );
  }

  Widget _buildSuccessScreen(TransactionSuccess state) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.check_circle, color: Colors.green, size: 64),
          const SizedBox(height: 16),
          const Text('Transfer Successful', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          Text('₹${state.amount.toStringAsFixed(2)}', style: const TextStyle(fontSize: 32)),
          const SizedBox(height: 8),
          Text('Transaction ID: ${state.transactionId}'),
          Text('To: ${state.beneficiaryName}'),
          const SizedBox(height: 32),
          CustomButton(
            onPressed: () {},
            child: const Text('Download Receipt'),
          ),
          const SizedBox(height: 8),
          CustomButton(
            onPressed: () {},
            child: const Text('Share Receipt'),
          ),
          const SizedBox(height: 8),
          CustomButton(
            onPressed: () {
              _resetForm();
              context.read<TransactionBloc>().add(ResetTransactionEvent());
            },
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorScreen(TransactionFailure state) {
    final isNetworkError = state.error.contains('Network');
    final isSessionError = state.error.contains('Session');
    
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error, color: Colors.red, size: 64),
          const SizedBox(height: 16),
          const Text('Transfer Failed', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          const SizedBox(height: 16),
          Text(state.error),
          if (isNetworkError) ...[
            const SizedBox(height: 8),
            const Text('Check your internet connection and try again'),
          ],
          if (isSessionError) ...[
            const SizedBox(height: 8),
            const Text('Please login again'),
          ],
          const SizedBox(height: 32),
          CustomButton(
            onPressed: () {
              if (isSessionError) {
                // Navigate to login
              } else {
                context.read<TransactionBloc>().add(RetryTransactionEvent());
              }
            },
            child: Text(isSessionError ? 'Login' : 'Retry'),
          ),
          const SizedBox(height: 8),
          CustomButton(
            onPressed: () {
              Navigator.pop(context);
            },
            child: const Text('Cancel'),
          ),
        ],
      ),
    );
  }
}
