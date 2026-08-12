# Glossary

This document defines the key terms and concepts used throughout the Expat Ledger project to ensure consistency across the team.

| Term                                   | Definition                                                                                                                                                                             |
| :------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tenant**                             | A top-level isolation unit representing a legal or personal financial entity (e.g., a family or an individual expat). All data (accounts, transactions) belongs to exactly one tenant. |
| **User Account**                       | An identity managed by Auth0. A user can have access to one or more Tenants with different roles.                                                                                      |
| **Ledger Account**                     | A financial account (Checking, Savings, Credit Card) tracked within the system. Not to be confused with a "User Account".                                                              |
| **Remittance**                         | A cross-border money transfer, typically involving currency conversion (e.g., sending USD from the US to a COP account in Colombia).                                                   |
| **Remittance Link**                    | The association between an outbound transaction in one currency/country and its corresponding inbound deposit in another currency/country.                                             |
| **FX (Foreign Exchange)**              | The process of converting one currency to another using an exchange rate.                                                                                                              |
| **Historical FX**                      | The exchange rate that was valid on a specific past date, used for calculating the historical value of transactions or balances.                                                       |
| **Reporting Currency**                 | The primary currency chosen by a Tenant for consolidated reporting and balance calculation (e.g., USD).                                                                                |
| **Native Currency**                    | The actual currency of a specific Ledger Account or Transaction (e.g., COP for a Colombian bank account).                                                                              |
| **Bank Attribution**                   | The process of identifying and tagging the originating or destination financial institution for a transaction.                                                                         |
| **Idempotency**                        | The property of an API operation where making the same request multiple times has the same effect as making it once.                                                                   |
| **ALE (Application-Level Encryption)** | Encrypting sensitive data fields within the application layer before they are sent to the database.                                                                                    |
