---
aliases:
- /observations/2017/12/06/psycopg2-transactions.html
categories: observations
date: '2017-12-06T13:58:16Z'
draft: false
showtoc: false
slug: psycopg2-transactions
title: Transaction Handling with Psycopg2
---

Databases are essential to most applications, however most database interaction is often overlooked by Python developers who use higher level libraries like Django or SQLAlchemy. We use and love PostgreSQL with Psycopg2, but I recently realized that I didn't have a good grasp on how exactly psycopg2 implemented core database concepts: particularly transaction isolation and thread safety.

Here's what the documentation says regarding transactions:

> Transactions are handled by the connection class. By default, the first time a command is sent to the database (using one of the cursors created by the connection), a new transaction is created. The following database commands will be executed in the context of the same transaction – not only the commands issued by the first cursor, but the ones issued by all the cursors created by the same connection. Should any command fail, the transaction will be aborted and no further command will be executed until a call to the rollback() method.

Transactions are therefore connection specific. When you create a connection, you can create multiple cursors, the transaction begins when the first cursor issues an `execute` -- all all commands executed by _all_ cursors after that are part of the same transaction until `commit` or `rollback`. After any of these methods are called, the next transaction is started on the next `execute` call.

This brings up a very important point:

> By default even a simple SELECT will start a transaction: in long-running programs, if no further action is taken, the session will remain “idle in transaction”, an undesirable condition for several reasons (locks are held by the session, tables bloat…). For long lived scripts, either make sure to terminate a transaction as soon as possible or use an autocommit connection.

This seems to indicate that when working directly with psycopg2, understanding transactions is essential to writing stable scripts. This post therefore details my notes and techniques for working more effectively with PostgreSQL from Python.

## Database Preliminaries

In order to demonstrate the code in this blog post, we need a database. The classic database example taught to undergraduates is that of a bank account, so we'll continue with that theme here! Sorry if this part is tedious, feel free to skip ahead. In a file, `schema.sql`, I defined the following schema as DDL (data definition language):

```sql
DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    pin SMALLINT NOT NULL
);


DROP TYPE IF EXISTS account_type CASCADE;
CREATE TYPE account_type AS ENUM ('checking', 'savings');

DROP TABLE IF EXISTS accounts CASCADE;
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    type account_type,
    owner_id INTEGER NOT NULL,
    balance NUMERIC DEFAULT 0.0,
    CONSTRAINT positive_balance CHECK (balance >= 0),
    FOREIGN KEY (owner_id) REFERENCES users (id)
);

DROP TYPE IF EXISTS ledger_type CASCADE;
CREATE TYPE ledger_type AS ENUM ('credit', 'debit');

DROP TABLE IF EXISTS ledger;
CREATE TABLE ledger (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    type ledger_type NOT NULL,
    amount NUMERIC NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts (id)
);
```

This creates a simple database with two tables. The owners table contains a PIN code for verification. Owners can have one or more accounts, and accounts have the constraint that the balance can never fall below $0.00. We can also seed the database with some initial data:

```sql
INSERT INTO users (id, username, pin) VALUES
    (1, 'alice', 1234),
    (2, 'bob', 9999);

INSERT INTO accounts (type, owner_id, balance) VALUES
    ('checking', 1, 250.0),
    ('savings', 1, 5.00),
    ('checking', 2, 100.0),
    ('savings', 2, 2342.13);
```

Moving to Python code we can add some template code to allow us to connect to the database and execute the SQL in our file above:

```python
import os
import psycopg2 as pg


def connect(env="DATABASE_URL"):
    url = os.getenv(env)
    if not url:
        raise ValueError("no database url specified")
    return pg.connect(url)


def createdb(conn, schema="schema.sql"):
    with open(schema, 'r') as f:
        sql = f.read()

    try:
        with conn.cursor() as curs:
            curs.execute(sql)
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
```

The `connect` function looks for the database connection string in the environment variable `$DATABASE_URL`. Because database configuration code can contain passwords and network information it is always best to store it in the environment or in a local, secure configuration file that can only be accessed by the process and not checked in with code. The connection string should look something like: `postgresql://user@localhost:5432/dbname`.

The `createdb` function reads the SQL from the `schema.sql` file and executes it against the database. Note this is why we have the `DROP TABLE IF EXISTS` statements, so we can guarantee we always start with a fresh database when we run this script. This function also gives us our first glance at transactions and database interaction with Python.

Complying with [PEP 249](https://www.python.org/dev/peps/pep-0249/) we create a connection to the database, then create a cursor from the connection. Cursors manage the execution of SQL against the database as well as data retrieval. We execute the SQL in our schema file, committing the transaction if no exceptions are raised, and rolling back if it fails. We will explore this more in the next section.

## Transaction Management

A transaction consists of one or more related operations that represent a single unit of work. For example, in the bank account example you might have a deposit transaction that executes queries to look up the account and verify the user, add a record to a list of daily deposits, check if the daily deposit limit has been reached, then modify the account balance. All of these operations represent all of the steps required to perform a deposit.

The goal of a transaction is that when the transaction is complete, the database remains in a single consistent state. Consistency is often defined by invariants or constraints that describe at a higher level how the database should maintain information. From a programming perspective, if those constraints are violated an exception is raised. For example, the database has a `positive_balance` constraint, if the balance for an account goes below zero an exception is raised. When this constraint is violated the database _must remain unchanged_ and all operations performed by the transaction must be _rolled back_. If the transaction was successful we can then _commit_ the changes, which guarantee that the database has successfully applied our operation.

So why do we need to manage transactions? Consider the following code:

```python
conn = connect()
curs = conn.cursor()

try:
    # Execute a command that will raise a constraint
    curs.execute("UPDATE accounts SET balance=%s", (-130.935,))
except Exception as e:
    print(e) # Constraint exception

# Execute another command, but because of the previous exception:
curs = conn.cursor()
try:
    curs.execute("SELECT id, type FROM accounts WHERE owner_id=%s", (1,))
except pg.InternalError as e:
    print(e)
```

The first `curs.execute` triggers the constraint exception, which is caught and printed. However, the database is now in an inconsistent state. When you try to execute the second query, a `psycopg2.InternalError` is raised: `"current transaction is aborted, commands ignored until end of transaction block"`. In order to continue with the application, `conn.rollback()` needs to be called to end the transaction and start a new one.

**NOTE**: Using `with conn.cursor() as curs:` causes the same behavior, the context manager does not automatically clean up the state of the transaction.

This essentially means all transactions can be wrapped in a `try` block, if they conclude successfully they can be committed, however if they raise an exception, they must be rolled back. A basic decorator that does this is as follows:

```python
from functools import wraps

def transaction(func):
    @wraps(func)
    def inner(*args, **kwargs):
        conn = connect()
        try:
            func(conn, *args, **kwargs)
            conn.commit()
        except Exception as e:
            conn.rollback()
            log.error("{} error: {}".format(func.__name__, e))
        finally:
            conn.close()
    return inner
```

This decorator wraps the specified function, returning an inner function that injects a new connection as the first argument to the decorated function. If the decorated function raises an exception, the transaction is rolled back and the error is logged.

The decorator method is nice but the connection injection can be a bit weird. An alternative is a [context manager](https://docs.python.org/3/library/contextlib.html) that ensures the connection is committed or rolled back in a similar fashion:

```python
from contextlib import contextmanager

@contextmanager
def transaction():
    try:
        conn = connect()
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        log.error("db error: {}".format(e))
    finally:
        conn.close()
```

This allows you to write code using `with` as follows:

```python
with transaction() as conn:
    # do transaction
```

The context manager allows you to easily compose two transactions inside a single function &mdash; of course this may be against the point. However, it is no problem to combine both the decorator and the context manager methods into two steps (more on this in isolation levels).

### ATM Application

So let's talk about two specific transactions for an imaginary database application: deposit and withdraw. Each of these operations has several steps:

1. Validate the user with the associated PIN
2. Ensure the user owns the account being modified
3. Write a ledger record with the credit or debit being applied
4. On credit, ensure the daily deposit limit isn't reached
5. Modify the balance of the account
6. Fetch the current balance to display to the user

Each transaction will perform 6-7 distinct SQL queries: `SELECT`, `INSERT`, and `UPDATE`. If any of them fails, then the database should remain completely unchanged. Failure in this case is that an exception is raised, which is potentially the easiest thing to do when you have a stack of functions calling other functions. Let's look at `deposit` first:

```python
@transaction
def deposit(conn, user, pin, account, amount):
    # Step 1: authenticate the user via pin and verify account ownership
    authenticate(conn, user, pin, account)

    # Step 2: add the ledger record with the credit
    ledger(conn, account, "credit", amount)

    # Step 3: update the account value by adding the amount
    update_balance(conn, account, amount)

    # Fetch the current balance in the account and log it
    record = "withdraw ${:0.2f} from account {} | current balance: ${:0.2f}"
    log.info(record.format(amount, account, balance(conn, account)))
```

This function simply calls other functions, passing the transaction context (in this case a connection as well as input details) to other functions which may or may not raise exceptions. Here are the two authenticate methods:

```python
def authenticate(conn, user, pin, account=None):
    """
    Returns an account id if the name is found and if the pin matches.
    """
    with conn.cursor() as curs:
        sql = "SELECT 1 AS authd FROM users WHERE username=%s AND pin=%s"
        curs.execute(sql, (user, pin))
        if curs.fetchone() is None:
            raise ValueError("could not validate user via PIN")
        return True

    if account:
        # Verify account ownership if account is provided
        verify_account(conn, user, account)


def verify_account(conn, user, account):
    """
    Verify that the account is held by the user.
    """
    with conn.cursor() as curs:
        sql = (
            "SELECT 1 AS verified FROM accounts a "
            "JOIN users u on u.id = a.owner_id "
            "WHERE u.username=%s AND a.id=%s"
        )
        curs.execute(sql, (user, account))

        if curs.fetchone() is None:
            raise ValueError("account belonging to user not found")
        return True
```

The `authenticate` and `verify_account` functions basically look in the database to see if there is a record that matches the conditions &mdash; a user with a matching PIN in `authenticate` and a `(user, account_id)` pair in `verify_account`. Both of these functions rely on the `UNIQUE` constraint in the database for usernames and account ids. This example shows how the function call stack can get arbitrarily deep; `verify_account` is called by `authenticate` which is called by `deposit`. By raising an exception at any point in the stack, the transaction will proceed no further, protecting us from harm later in the transaction.

Note also that neither of these functions have an `@transaction` decorator, this is because it is expected that they are called from within another transaction. They are independent operations, but they can be called independently in a transaction with the context manager.

Next we insert a ledger record:

```python
MAX_DEPOSIT_LIMIT = 1000.00

def ledger(conn, account, record, amount):
    """
    Add a ledger record with the amount being credited or debited.
    """
    # Perform the insert
    with conn.cursor() as curs:
        sql = "INSERT INTO ledger (account_id, type, amount) VALUES (%s, %s, %s)"
        curs.execute(sql, (account, record, amount))

    # If we are crediting the account, perform daily deposit verification
    if record == "credit":
        check_daily_deposit(conn, account)

def check_daily_deposit(conn, account):
    """
    Raise an exception if the deposit limit has been exceeded.
    """
    with conn.cursor() as curs:
        sql = (
            "SELECT amount FROM ledger "
            "WHERE date=now()::date AND type='credit' AND account_id=%s"
        )
        curs.execute(sql, (account,))
        total = sum(row[0] for row in curs.fetchall())
        if total > MAX_DEPOSIT_LIMIT:
            raise Exception("daily deposit limit has been exceeded!")
```

This is the first place that we modify the state of the database by inserting a ledger record. If, when we `check_daily_deposit`, we discover that our deposit limit has been exceeded for the day, an exception is raised that will `rollback` the transaction. This will ensure that the ledger record is not accidentally stored on disk. Finally we update the account balance:

```python
def update_balance(conn, account, amount):
    """
    Add the amount (or subtract if negative) to the account balance.
    """
    amount = Decimal(amount)
    with conn.cursor() as curs:
        current = balance(conn, account)
        sql = "UPDATE accounts SET balance=%s WHERE id=%s"
        curs.execute(sql, (current+amount, account))


def balance(conn, account):
    with conn.cursor() as curs:
        curs.execute("SELECT balance FROM accounts WHERE id=%s", (account,))
        return curs.fetchone()[0]
```

I'll have more to say on `update_balance` when we discuss isolation levels, but suffice it to say, this is another place where if the transaction fails we want to ensure that our account is not modified! In order to complete the example, here is the `withdraw` transaction:

```python
@transaction
def withdraw(conn, user, pin, account, amount):
    # Step 1: authenticate the user via pin and verify account ownership
    authenticate(conn, user, pin, account)

    # Step 2: add the ledger record with the debit
    ledger(conn, account, "debit", amount)

    # Step 3: update the account value by subtracting the amount
    update_balance(conn, account, amount * -1)

    # Fetch the current balance in the account and log it
    record = "withdraw ${:0.2f} from account {} | current balance: ${:0.2f}"
    log.info(record.format(amount, account, balance(conn, account)))
```

This is similar but modifies the inputs to the various operations to decrease the amount of the account by a debit ledger record. We can run:

```python
if __name__ == '__main__':
    conn = connect()
    createdb(conn)

    # Successful deposit
    deposit('alice', 1234, 1, 785.0)

    # Successful withdrawal
    withdraw('alice', 1234, 1, 230.0)

    # Unsuccessful deposit
    deposit('alice', 1234, 1, 489.0)

    # Successful deposit
    deposit('bob', 9999, 2, 220.23)
```

And we should see the following log records:

```
2017-12-06 20:01:00,086 withdraw $785.00 from account 1 | current balance: $1035.00
2017-12-06 20:01:00,094 withdraw error: could not validate user via PIN
2017-12-06 20:01:00,103 withdraw $230.00 from account 1 | current balance: $805.00
2017-12-06 20:01:00,118 deposit error: daily deposit limit has been exceeded!
2017-12-06 20:01:00,130 withdraw $220.23 from account 2 | current balance: $225.23
```

This should set a baseline for creating simple and easy to use transactions in Python. However, if you remember your databases class as an undergraduate, things get more interesting when two transactions are occurring at the same time. We'll explore that from a single process by looking at multi-threaded database connections.

## Threads

Let's consider how to run two transactions at the same time from within the same application. The simplest way to do this is to use the `threading` library to execute transactions simultaneously. How do you achieve thread safety when accessing the database? Back to the docs:

> Connection objects are thread-safe: many threads can access the same database either using separate sessions and creating a connection per thread or using the same connection and creating separate cursors. In DB API 2.0 parlance, Psycopg is level 2 thread safe.

This means that every thread must have its own `conn` object (which explore in the connection pool section). Any cursor created from the same connection object will be in the same transaction no matter the thread. We also want to consider how each transaction influences each other, and we'll take a look at that first by exploring isolation levels and session state.

### Session State

Let's say that Alice and Charlie have a joint account, under Alice's name. They both show up to ATMs at the same time, Alice tries to deposit $75 and then withdraw $25 and Charlie attempts to withdraw $300. We can simulate this with threads as follows:

```python
import time
import random
import threading

def op1():
    time.sleep(random.random())
    withdraw('alice', 1234, 1, 300.0)

def op2():
    time.sleep(random.random())
    deposit('alice', 1234, 1, 75.0)
    withdraw('alice', 1234, 1, 25.0)


threads = [
    threading.Thread(target=op1),
    threading.Thread(target=op2),
]

for t in threads:
    t.start()

for t in threads:
    t.join()
```

Depending on the timing, one of two things can happen. Charlie can get rejected as not having enough money in his account, and the final state of the database can be $300 or all transaction can succeed with the final state of the database set to $0. There are three transactions happening, two `withdraw` transactions and a `deposit`. Each of these transactions runs in _isolation_, meaning that they see the database how they started and any changes that they make; so if Charlie's `withdraw` and Alice's `deposit` happen simultaneously, Charlie will be rejected since it doesn't know about the deposit until it's finished. No matter what, the database will be left in the same state.

However, for performance reasons, you may want to modify the isolation level for a particular transaction. Possible levels are as follows:

1. `READ UNCOMMITTED`: lowest isolation level, transaction may read values that are not yet committed (and may never be committed).
2. `READ COMMITTED`: write locks are maintained but read locks are released after select, meaning two different values can be read in different parts of the transaction.
3. `REPEATABLE READ`: keep both read and write locks so multiple reads return same values but [phantom reads](https://en.wikipedia.org/wiki/Isolation_(database_systems)#Phantom_reads) can occur.
4. `SERIALIZABLE`: the highest isolation level: read, write, and range locks are maintained until the end of the transaction.
5. `DEFAULT`: set by server configuration not Python, usually `READ COMMITTED`.

Note that as the isolation level increases, the number of locks being maintained also increases, which severely impacts performance if there is lock contention or deadlocks. It is possible to set the isolation level on a _per-transaction_ basis in order to improve performance of all transactions happening concurrently. To do this we must modify the _session_ parameters on the connection, which modify the behavior of the transaction or statements that follow in that particular session. Additionally we can set the session to `readonly`, which does not allow writes to temporary tables (for performance and security) or to `deferrable`.

Deferrability is very interesting in a transaction, because it modifies how database constraints are checked. Non-deferrable transactions immediately check the constraint after a statement is executed. This means that `UPDATE accounts SET balance=-5.45` will immediately raise an exception. Deferrable transactions however wait until the transaction is concluded before checking the constraints. This allows you to write multiple overlapping operations that may put the database into a correct state by the end of the transaction, but potentially not during the transaction (this also overlaps with the performance of various isolation levels).

In order to change the session, we'll use a context manager as we did before to modify the session for the transaction, then reset the session back to the defaults:

```python
@contextmanager
def session(conn, isolation_level=None, readonly=None, deferrable=None):
    try:
        conn.set_session(
            isolation_level=isolation_level,
            readonly=readonly,
            deferrable=deferrable
        )
        yield conn
    finally:
        # Reset the session to defaults
        conn.set_session(None, None, None, None)
```

We can then use `with` to conduct transactions with different isolation levels:

```python
with transaction() as conn:
    with session(conn, isolation_level="READ COMMITTED") as conn:
        # Do transaction
```

**NOTE**: There cannot be an ongoing transaction when the session is set therefore it is more common for me to set the isolation level, readonly, and deferrable inside of the transaction decorator, rather than using two separate context managers as shown above. Frankly, it is also common to set these properties on a per-process basis rather than on a per-transaction basis, therefore the session is set in `connect`.

### Connection Pools

Connections cannot be shared across threads. In the threading example above, if we remove the `@transaction` decorator and pass the same connection into both operations as follows:

```python
conn = connect()

def op1():
    time.sleep(random.random())
    withdraw(conn, 'alice', 1234, 1, 300.0)

def op2():
    time.sleep(random.random())
    deposit(conn, 'alice', 1234, 1, 75.0)
    withdraw(conn, 'alice', 1234, 1, 25.0)
```

If the `op1` withdraw fires first, the exception will cause all of the `op2` statements to also fail, since its in the same transaction. This essentially means that _both op1 and op2 are in the same transaction even though they are in different threads!_

We've avoided this so far by creating a new connection every time a transaction runs. However, connecting to the database can be expensive and in high-transaction workloads we may want to simply keep the connection open, but ensure they are only used by one transaction at a time. The solution is to use _connection pools_. We can modify our connect function as follows:

```python
from psycopg2.pool import ThreadedConnectionPool

def connect(env="DATABASE_URL", connections=2):
    """
    Connect to the database using an environment variable.
    """
    url = os.getenv(env)
    if not url:
        raise ValueError("no database url specified")

    minconns = connections
    maxconns = connections * 2
    return ThreadedConnectionPool(minconns, maxconns, url)
```

This creates a thread-safe connection pool that establishes at least 2 connections and will go up to a maximum of 4 connections on demand. In order to use the pool object in our transaction decorator, we will have to connect when the decorator is imported, creating a global pool object:

```python
pool = connect()

@contextmanager
def transaction(name="transaction", **kwargs):
    # Get the session parameters from the kwargs
    options = {
        "isolation_level": kwargs.get("isolation_level", None),
        "readonly": kwargs.get("readonly", None),
        "deferrable": kwargs.get("deferrable", None),
    }

    try:
        conn = pool.getconn()
        conn.set_session(**options)
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        log.error("{} error: {}".format(name, e))
    finally:
        conn.reset()
        pool.putconn(conn)
```

Using `pool.getconn` retrieves a connection from the pool (if one is available, blocking until one is ready), then when we're done we can `pool.putconn` to release the connection object.

## Conclusion

This has been a ton of notes on more direct usage of psycopg2. Sorry I couldn't write a more conclusive conclusion but it's late and this post is now close to 4k words. Time to go get dinner!

## Notes

I used logging as the primary output to this application. The logging was set up as follows:

```python
import logging

LOG_FORMAT = "%(asctime)s %(message)s"

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
log = logging.getLogger('balance')
```

For the complete code, see this [gist](https://gist.github.com/bbengfort/936b4b3db9d81d27204a81f6ad816e5d).
