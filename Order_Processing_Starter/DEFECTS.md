# Defects Identified and Corrections

## 1. Duplicate Orders Due to Non-Unique Request IDs

**Defect:** The `request_id` was not unique. If a client retried a checkout request due to a network error, the same order could be processed and stored more than once. This could also cause inventory stock to be deducted multiple times.

**Corrections:**
- Added a `UNIQUE` constraint to the `request_id` column in the orders table.
- Added a `get_order_by_request_id()` helper method in `repository.py`.
- Updated `checkout.py` to check whether a request ID has already been processed before creating another order.

## 2. Cart and Inventory Handling When Stock Is Unavailable

**Defect:** When an item was unavailable, the checkout process did not properly preserve the customer's cart. Previously added items could be lost even when the checkout failed.

**Corrections:**
- Added repository methods to reserve and release inventory stock.
- Updated `checkout.py` to check whether sufficient stock is available before proceeding with payment.
- If stock reservation fails, checkout returns an `out_of_stock` result without clearing the cart.

## 3. Incorrect Discount and Total Calculations

**Defect:** Discounts were not calculated correctly when additional items were added to the cart after applying a discount. The discounted total did not properly reflect the updated subtotal.

**Corrections:**
- Fixed the subtotal calculation to include all current cart items.
- Updated the discount calculation so it is based on the current subtotal.
- Added a shipping fee calculation.
- Added support for the `FREESHIP` discount code, which removes the shipping fee.

## 4. Missing Cart Quantity Validation

**Defect:** The `add_item()` and `remove_item()` methods in `cart.py` did not properly validate quantities. Negative numbers, zero, decimals, and other invalid values could be provided.

**Corrections:**
- Added a `_valid_quantity()` validation method in `cart.py`.
- Updated `add_item()` and `remove_item()` to accept only positive whole-number quantities.
- Invalid quantities are rejected without modifying the cart.
- Removing a quantity equal to or greater than the current cart quantity removes the item from the cart.

## 5. Incorrect Saved Cart Loading Behaviour

**Defect:** The `load()` method in `cart.py` added saved items on top of existing cart items instead of replacing them. Reloading the saved cart could therefore result in duplicate quantities. Additionally, unavailable or unknown saved items were not properly reported.

**Corrections:**
- Updated `load()` to clear the existing in-memory cart before loading saved items.
- Added handling for unknown products and items with insufficient stock.
- Unavailable saved items are skipped and their SKUs are returned so they can be reported.

## 6. Orders Not Properly Filtered by User

**Defect:** The order-listing method returned orders belonging to all users instead of restricting the results to the requested user. This could expose other users' order information, including payment status and order amounts.

**Corrections:**
- Updated the order-listing method in `repository.py` to filter orders using `user_id`.
- Ensured the database connection is closed after retrieving the results.

## 7. SQL Injection Vulnerabilities

**Defect:** The `get_product()` and `get_saved_cart()` methods used unsafe SQL queries. Malicious inputs, such as SQL injection payloads, could potentially modify the query and access unintended database information.

**Corrections:**
- Updated `get_product()` to use parameterized SQL queries for SKU values.
- Updated `get_saved_cart()` to use parameterized SQL queries for user IDs.
- This ensures user-provided values are treated as data rather than executable SQL commands.

## 8. Sensitive Payment Information in Console Logs

**Defect:** The application printed payment tokens in the console logs. Payment tokens are sensitive information and should not be exposed in application logs.

**Corrections:**
- Removed the statement that printed the payment token.
- Prevented sensitive payment information from being unnecessarily exposed through console logging.