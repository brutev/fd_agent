import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';

import 'package:fd_agent_mobile/features/transactions/presentation/pages/neft_transfer_page.dart';
import 'package:fd_agent_mobile/features/transactions/presentation/bloc/transaction_bloc.dart';
import 'package:fd_agent_mobile/features/transactions/domain/entities/beneficiary.dart';
import 'package:fd_agent_mobile/shared/widgets/custom_button.dart';
import 'package:fd_agent_mobile/shared/widgets/custom_text_field.dart';

import 'neft_transfer_test.mocks.dart';

@GenerateMocks([TransactionBloc])
void main() {
  late MockTransactionBloc mockTransactionBloc;

  setUp(() {
    mockTransactionBloc = MockTransactionBloc();
    when(mockTransactionBloc.state).thenReturn(TransactionInitial());
    when(mockTransactionBloc.stream).thenAnswer((_) => Stream.empty());
  });

  Widget createWidgetUnderTest() {
    return MaterialApp(
      home: BlocProvider<TransactionBloc>(
        create: (context) => mockTransactionBloc,
        child: const NEFTTransferPage(),
      ),
    );
  }

  group('NEFT Transfer Page Widget Tests', () {
    testWidgets('should render NEFT form correctly', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Verify page title
      expect(find.text('NEFT Transfer'), findsOneWidget);

      // Verify form fields
      expect(find.byType(CustomTextField), findsNWidgets(4)); // Beneficiary, IFSC, Account, Amount
      expect(find.text('Select Beneficiary'), findsOneWidget);
      expect(find.text('IFSC Code'), findsOneWidget);
      expect(find.text('Account Number'), findsOneWidget);
      expect(find.text('Amount'), findsOneWidget);
      expect(find.text('Remarks (Optional)'), findsOneWidget);

      // Verify transfer button
      expect(find.byType(CustomButton), findsOneWidget);
      expect(find.text('Transfer'), findsOneWidget);
    });

    testWidgets('should show beneficiary selection dropdown', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Tap on beneficiary dropdown
      await tester.tap(find.text('Select Beneficiary'));
      await tester.pumpAndSettle();

      // Should show dropdown options
      expect(find.byType(DropdownMenuItem), findsWidgets);
    });

    testWidgets('should validate IFSC code input', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Find IFSC field and enter invalid IFSC
      final ifscField = find.widgetWithText(CustomTextField, 'IFSC Code');
      await tester.enterText(ifscField, 'INVALID');
      await tester.pump();

      // Tap transfer button to trigger validation
      await tester.tap(find.text('Transfer'));
      await tester.pump();

      // Should show validation error
      expect(find.text('Invalid IFSC code format'), findsOneWidget);
    });

    testWidgets('should validate account number input', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Find account number field and enter invalid account
      final accountField = find.widgetWithText(CustomTextField, 'Account Number');
      await tester.enterText(accountField, '123');
      await tester.pump();

      // Tap transfer button to trigger validation
      await tester.tap(find.text('Transfer'));
      await tester.pump();

      // Should show validation error
      expect(find.text('Account number must be 9-18 digits'), findsOneWidget);
    });

    testWidgets('should validate amount input with NEFT limits', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Test minimum amount validation
      final amountField = find.widgetWithText(CustomTextField, 'Amount');
      await tester.enterText(amountField, '0.5');
      await tester.pump();

      await tester.tap(find.text('Transfer'));
      await tester.pump();

      expect(find.text('Amount must be at least ₹1.00'), findsOneWidget);

      // Test maximum amount validation
      await tester.enterText(amountField, '2000000');
      await tester.pump();

      await tester.tap(find.text('Transfer'));
      await tester.pump();

      expect(find.text('Amount cannot exceed ₹10,00,000.00'), findsOneWidget);
    });

    testWidgets('should show confirmation screen on valid input', (WidgetTester tester) async {
      // Mock successful validation state
      when(mockTransactionBloc.state).thenReturn(TransactionValidated());

      await tester.pumpWidget(createWidgetUnderTest());

      // Fill valid data
      await tester.enterText(find.widgetWithText(CustomTextField, 'IFSC Code'), 'SBIN0000001');
      await tester.enterText(find.widgetWithText(CustomTextField, 'Account Number'), '1234567890123456');
      await tester.enterText(find.widgetWithText(CustomTextField, 'Amount'), '50000');
      await tester.pump();

      // Tap transfer button
      await tester.tap(find.text('Transfer'));
      await tester.pumpAndSettle();

      // Should navigate to confirmation screen
      expect(find.text('Confirm Transfer'), findsOneWidget);
      expect(find.text('₹50,000.00'), findsOneWidget);
      expect(find.text('SBIN0000001'), findsOneWidget);
    });

    testWidgets('should show OTP verification step', (WidgetTester tester) async {
      // Mock OTP required state
      when(mockTransactionBloc.state).thenReturn(TransactionOTPRequired());

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show OTP input screen
      expect(find.text('Enter OTP'), findsOneWidget);
      expect(find.text('OTP sent to your registered mobile number'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget); // OTP input field
      expect(find.text('Verify OTP'), findsOneWidget);
      expect(find.text('Resend OTP'), findsOneWidget);
    });

    testWidgets('should show MPIN verification as fallback', (WidgetTester tester) async {
      // Mock MPIN required state
      when(mockTransactionBloc.state).thenReturn(TransactionMPINRequired());

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show MPIN input screen
      expect(find.text('Enter MPIN'), findsOneWidget);
      expect(find.text('Enter your 4-digit MPIN'), findsOneWidget);
      expect(find.byType(TextField), findsOneWidget); // MPIN input field
      expect(find.text('Verify MPIN'), findsOneWidget);
    });

    testWidgets('should show success screen with receipt', (WidgetTester tester) async {
      // Mock success state
      when(mockTransactionBloc.state).thenReturn(
        TransactionSuccess(
          transactionId: 'TXN123456789',
          amount: 50000.0,
          beneficiaryName: 'John Doe',
          timestamp: DateTime.now(),
        ),
      );

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show success screen
      expect(find.text('Transfer Successful'), findsOneWidget);
      expect(find.text('₹50,000.00'), findsOneWidget);
      expect(find.text('TXN123456789'), findsOneWidget);
      expect(find.text('John Doe'), findsOneWidget);
      expect(find.text('Download Receipt'), findsOneWidget);
      expect(find.text('Share Receipt'), findsOneWidget);
      expect(find.text('Done'), findsOneWidget);
    });

    testWidgets('should show failure screen with retry option', (WidgetTester tester) async {
      // Mock failure state
      when(mockTransactionBloc.state).thenReturn(
        TransactionFailure(error: 'Insufficient balance'),
      );

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show failure screen
      expect(find.text('Transfer Failed'), findsOneWidget);
      expect(find.text('Insufficient balance'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
      expect(find.text('Cancel'), findsOneWidget);
    });

    testWidgets('should handle back button behavior correctly', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Should have back button in app bar
      expect(find.byType(BackButton), findsOneWidget);

      // Tap back button
      await tester.tap(find.byType(BackButton));
      await tester.pumpAndSettle();

      // Should navigate back (in real app, would pop the route)
      // Here we just verify the button exists and is tappable
    });

    testWidgets('should reset form after successful transaction', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Fill form
      await tester.enterText(find.widgetWithText(CustomTextField, 'IFSC Code'), 'SBIN0000001');
      await tester.enterText(find.widgetWithText(CustomTextField, 'Amount'), '50000');
      await tester.pump();

      // Mock success and then reset
      when(mockTransactionBloc.state).thenReturn(TransactionSuccess(
        transactionId: 'TXN123',
        amount: 50000.0,
        beneficiaryName: 'Test',
        timestamp: DateTime.now(),
      ));
      await tester.pump();

      // Tap Done button
      await tester.tap(find.text('Done'));
      await tester.pumpAndSettle();

      // Form should be reset
      final ifscField = tester.widget<TextField>(
        find.descendant(
          of: find.widgetWithText(CustomTextField, 'IFSC Code'),
          matching: find.byType(TextField),
        ),
      );
      expect(ifscField.controller?.text, isEmpty);
    });

    testWidgets('should show loading indicator during transaction', (WidgetTester tester) async {
      // Mock loading state
      when(mockTransactionBloc.state).thenReturn(TransactionLoading());

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show loading indicator
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('Processing Transaction...'), findsOneWidget);

      // Transfer button should be disabled
      final button = tester.widget<CustomButton>(find.byType(CustomButton));
      expect(button.onPressed, isNull);
    });

    testWidgets('should validate remarks field', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Enter invalid remarks (too long)
      final remarksField = find.widgetWithText(CustomTextField, 'Remarks (Optional)');
      await tester.enterText(remarksField, 'A' * 51); // 51 characters
      await tester.pump();

      await tester.tap(find.text('Transfer'));
      await tester.pump();

      expect(find.text('Remarks cannot exceed 50 characters'), findsOneWidget);

      // Enter invalid characters
      await tester.enterText(remarksField, 'Payment@#\$%');
      await tester.pump();

      await tester.tap(find.text('Transfer'));
      await tester.pump();

      expect(find.text('Remarks contain invalid characters'), findsOneWidget);
    });

    testWidgets('should handle network error gracefully', (WidgetTester tester) async {
      // Mock network error state
      when(mockTransactionBloc.state).thenReturn(
        TransactionFailure(error: 'Network connection failed'),
      );

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show network error message
      expect(find.text('Network connection failed'), findsOneWidget);
      expect(find.text('Check your internet connection and try again'), findsOneWidget);
      expect(find.text('Retry'), findsOneWidget);
    });

    testWidgets('should show transaction limits info', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Should show limits information
      expect(find.text('NEFT Limits: ₹1 - ₹10,00,000'), findsOneWidget);
      expect(find.text('Operating Hours: 8:00 AM - 7:00 PM'), findsOneWidget);
    });

    testWidgets('should handle beneficiary selection', (WidgetTester tester) async {
      // Mock beneficiaries loaded state
      final beneficiaries = [
        Beneficiary(
          id: '1',
          name: 'John Doe',
          accountNumber: '1234567890123456',
          ifscCode: 'SBIN0000001',
          bankName: 'State Bank of India',
        ),
        Beneficiary(
          id: '2',
          name: 'Jane Smith',
          accountNumber: '9876543210987654',
          ifscCode: 'HDFC0000001',
          bankName: 'HDFC Bank',
        ),
      ];

      when(mockTransactionBloc.state).thenReturn(
        BeneficiariesLoaded(beneficiaries: beneficiaries),
      );

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Tap beneficiary dropdown
      await tester.tap(find.text('Select Beneficiary'));
      await tester.pumpAndSettle();

      // Should show beneficiary options
      expect(find.text('John Doe'), findsOneWidget);
      expect(find.text('Jane Smith'), findsOneWidget);

      // Select a beneficiary
      await tester.tap(find.text('John Doe'));
      await tester.pumpAndSettle();

      // IFSC and Account fields should be auto-filled
      expect(find.text('SBIN0000001'), findsOneWidget);
      expect(find.text('1234567890123456'), findsOneWidget);
    });

    testWidgets('should show add beneficiary option', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Should have add beneficiary button
      expect(find.text('Add New Beneficiary'), findsOneWidget);

      // Tap add beneficiary
      await tester.tap(find.text('Add New Beneficiary'));
      await tester.pumpAndSettle();

      // Should navigate to add beneficiary screen
      // (In real app, would navigate to AddBeneficiaryPage)
    });

    testWidgets('should handle session timeout', (WidgetTester tester) async {
      // Mock session timeout state
      when(mockTransactionBloc.state).thenReturn(
        TransactionFailure(error: 'Session expired'),
      );

      await tester.pumpWidget(createWidgetUnderTest());
      await tester.pump();

      // Should show session timeout message
      expect(find.text('Session expired'), findsOneWidget);
      expect(find.text('Please login again'), findsOneWidget);
      expect(find.text('Login'), findsOneWidget);
    });
  });

  group('NEFT Transfer Page Integration Tests', () {
    testWidgets('should complete full NEFT transfer flow', (WidgetTester tester) async {
      await tester.pumpWidget(createWidgetUnderTest());

      // Step 1: Fill form
      await tester.enterText(find.widgetWithText(CustomTextField, 'IFSC Code'), 'SBIN0000001');
      await tester.enterText(find.widgetWithText(CustomTextField, 'Account Number'), '1234567890123456');
      await tester.enterText(find.widgetWithText(CustomTextField, 'Amount'), '50000');
      await tester.enterText(find.widgetWithText(CustomTextField, 'Remarks (Optional)'), 'Salary payment');
      await tester.pump();

      // Step 2: Submit form
      await tester.tap(find.text('Transfer'));
      await tester.pumpAndSettle();

      // Verify form submission event
      verify(mockTransactionBloc.add(any)).called(1);

      // Step 3: Mock confirmation state
      when(mockTransactionBloc.state).thenReturn(TransactionValidated());
      await tester.pump();

      // Should show confirmation screen
      expect(find.text('Confirm Transfer'), findsOneWidget);

      // Step 4: Confirm transaction
      await tester.tap(find.text('Confirm'));
      await tester.pumpAndSettle();

      // Step 5: Mock OTP state
      when(mockTransactionBloc.state).thenReturn(TransactionOTPRequired());
      await tester.pump();

      // Enter OTP
      await tester.enterText(find.byType(TextField), '123456');
      await tester.tap(find.text('Verify OTP'));
      await tester.pumpAndSettle();

      // Step 6: Mock success state
      when(mockTransactionBloc.state).thenReturn(TransactionSuccess(
        transactionId: 'TXN123456789',
        amount: 50000.0,
        beneficiaryName: 'Test Beneficiary',
        timestamp: DateTime.now(),
      ));
      await tester.pump();

      // Should show success screen
      expect(find.text('Transfer Successful'), findsOneWidget);
      expect(find.text('TXN123456789'), findsOneWidget);
    });
  });
}