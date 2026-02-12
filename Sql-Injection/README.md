# Web Security: SQL Injection (SQLi)

SQL injection (SQLi) is a web security vulnerability that allows an attacker to interfere with the queries that an application makes to its database. This can allow an attacker to view data that they are not normally able to retrieve. This might include data that belongs to other users, or any other data that the application can access. In many cases, an attacker can modify or delete this data, causing persistent changes to the application's content or behavior.

In some situations, an attacker can escalate a SQL injection attack to compromise the underlying server or other back-end infrastructure. It can also enable them to perform denial-of-service attacks.

## SQL Injection Types

![Types of SQL Injection](https://raw.githubusercontent.com/Shubhankargupta691/Web-Security/refs/heads/main/Sql-Injection/assets/Sql%20Inection.png)

### 1. In-band SQLi (Classic)
The attacker uses the same communication channel to launch the attack and gather results.
*   **Error-based SQLi:** Relies on database error messages to reveal info about the structure.
*   **Union-based SQLi:** Uses the `UNION` SQL operator to combine results from multiple tables into a single HTTP response.

### 2. Inferential SQLi (Blind)
No data is actually transferred via the web application. Instead, the attacker reconstructs the database structure by sending payloads and observing the response.
*   **Boolean-based:** Observes whether the application returns a different HTTP response (e.g., a "Welcome" message vs. an "Error" message).
*   **Time-based:** Relies on the database pausing for a specific amount of time before responding.

### 3. Out-of-band SQLi
The attacker uses a different communication channel to get the results (e.g., triggering a DNS or HTTP request to a server they control). This is used when the application is too secure for blind or in-band attacks.

## Prevention
*   Use **Parameterized Queries** (Prepared Statements).
*   Implement **Input Validation** (Allow-listing).
*   Follow the **Principle of Least Privilege** for database accounts.

---
*For more information, check the [OWASP Top 10](https://owasp.org).*
