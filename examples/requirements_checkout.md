# E-Commerce Checkout Process

## Overview
The checkout process allows users to purchase items from their shopping cart.

## User Story
As a registered user, I want to complete a purchase so that I can receive my items.

## Functional Requirements

### Cart Review
- Display all items with name, quantity, unit price, and subtotal
- Users can update quantity (1-99) for each item
- Users can remove items from the cart
- Display cart total (sum of all subtotals)
- "Continue Shopping" and "Proceed to Checkout" buttons

### Shipping Information
- Collect: full name, address line 1, address line 2 (optional), city, state, zip code, phone number
- All fields required except address line 2
- Zip code must be valid US format (5 digits or 5+4)
- Phone must be valid US format (10 digits)
- Option to save address for future orders

### Payment
- Accept credit card (Visa, MasterCard, Amex)
- Card number: 13-19 digits, validated with Luhn algorithm
- Expiration date: MM/YY format, must be future date
- CVV: 3 digits for Visa/MC, 4 digits for Amex
- Display accepted card logos
- Billing address same as shipping (default) or different

### Order Confirmation
- Display order summary with all items, shipping, tax, and total
- Generate unique order number
- Send confirmation email
- Deduct inventory for purchased items

## Business Rules
- Minimum order amount: $10.00
- Free shipping for orders over $50
- Tax rate based on shipping state
- Out-of-stock items cannot be purchased
