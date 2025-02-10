prompts = {

# PE1: Dialect + Tables Name + NLQ
"simple_prompt_1":
"""You are a {dialect} expert, your task is to create an optimal, syntactically, and semantically correct {dialect} query based on the provided database tables to answer the input question.

Only use the following tables:
{tables}

Input question:
{nlq}

Provide only the SQL query to execute without any comments, and ensure it ends with a semicolon.""",

# PE2: Dialect + Completed Schema + NLQ
"simple_prompt_2":
"""You are a {dialect} expert, your task is to create an optimal, syntactically, and semantically correct {dialect} query based on the provided database schema to answer the input question.

Consider the following database schema:
{schema}

Input question:
{nlq}

Provide only the SQL query to execute without any comments, and ensure it ends with a semicolon.""",

# PE3: Dialect + SQL Style + Completed Schema + NLQ
"medium_prompt_1":
"""You are a {dialect} expert, your task is to create an optimal, syntactically, and semantically correct {dialect} query based on the provided database schema and the specified SQL guidelines to answer the input question.

### Database Schema

{schema}

### SQL Style Guidelines

Always use the proper names of tables and columns instead of IDs, unless IDs are explicitly requested. Extract table names, column names, relationships, and data types exclusively from the schema, and avoid querying non-existent columns or tables. Prefer JOINs over subqueries for combining tables. Ensure the field or column you intend to use belongs to the corresponding table. Use table aliases for all columns to enhance clarity and readability, ensuring each column referenced corresponds to its table alias. Apply appropriate aliases for new columns based on the input question. Prefer LIKE over '=' for comparisons. Utilize the julianday function for date calculations. Always use table aliases when the query involves two or more tables. Use named columns and filter columns in the SELECT statement. Employ BETWEEN to filter an interval of dates or values, including both date and time in ranges where required. Ensure appropriate column IDs are included in the queries. Use ROUND if the input question specifies it.

### Input Question

{nlq}

Provide only the SQL query to execute without any comments, and ensure it ends with a semicolon.""",

# PE4: Dialect + Completed Schema + Five Examples NLQ-SQL + NLQ (Nativo).
"medium_prompt_2":
"""You are a {dialect} expert, your task is to create an optimal, syntactically, and semantically correct {dialect} query based on the provided database schema and five example pairs of NLQ (input question) - SQL, to answer the input question.

### Database Schema

{schema}

### Example NLQ-SQL Pairs

NLQ: Tell me the name of the movies of the actor CHRISTIAN AKROYD ordered by category.
SQL:
SELECT f.film_id, f.title, a.first_name, a.last_name, c.name
FROM film f
JOIN film_actor fa ON f.film_id = fa.film_id
JOIN actor a ON fa.actor_id = a.actor_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE a.first_name LIKE 'CHRISTIAN' AND a.last_name LIKE 'AKROYD'
ORDER BY c.name;

NLQ: List the total sales that Mike had in the month of June 2005. Round the value to 4 decimal places.
SQL:
SELECT s.staff_id, s.first_name, s.last_name, ROUND(SUM(p.amount), 4) AS total_sales
FROM payment p
JOIN staff s ON p.staff_id = s.staff_id
WHERE s.first_name LIKE 'Mike'
AND p.payment_date BETWEEN '2005-06-01 00:00:00' AND '2005-06-30 23:59:59'
GROUP BY s.staff_id, s.first_name, s.last_name;

NLQ: Which customers have rented more than 35 movies at store 2?
SQL:
SELECT c.customer_id, c.first_name, c.last_name, COUNT(*) AS rental_count, c.store_id
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
WHERE c.store_id = 2
GROUP BY c.customer_id
HAVING COUNT(*) > 35;

NLQ: How many movie copies are in English? Organize it by category.
SQL:
SELECT c.name, COUNT(*) AS copy_count
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
JOIN language l ON f.language_id = l.language_id
WHERE l.name LIKE 'English'
GROUP BY c.name;

NLQ: List all unique cities where rentals have taken place.
SQL:
SELECT DISTINCT ci.city 
FROM city ci
JOIN address a ON ci.city_id = a.city_id
JOIN customer c ON a.address_id = c.address_id
JOIN rental r ON c.customer_id = r.customer_id;

### Input Question

{nlq}

Provide only the SQL query to execute without any comments, and ensure it ends with a semicolon.""",

# PE5: Dialect + Simple Guidelines + Completed Schema + three rows per table + NLQ (Nativo).
"complex_prompt_1":
"""You are a {dialect} expert, your task is to create an optimal, syntactically and semantically correct {dialect} query based on the provided database schema and the initial three rows of each table. Strictly retrieve table names, column names, relationships, and data types from the schema only. Analyze the first three rows of each table to ascertain column data types and sample content. Utilize this information to create a precise SQL query that answers the provided input question. Ensure all 'Between' conditions involving dates include both date and time components. Avoid using tables or columns outside the given schema.

### Database Schema and Sample Data

{table_info}

### Input Question

{nlq}

Provide only the SQL query to execute without any comments, and ensure it ends with a semicolon.""",

# PE6: Dialect + Medium Guidelines + Completed Schema + three rows per table + Five Examples NLQ-SQL + NLQ (Nativo).
"complex_prompt_2":
"""You are a {dialect} expert, your task is to create an optimal, syntactically and semantically correct {dialect} query based on the provided database schema, including the initial three rows of each table and five pairs of NLQ (natural language question) - SQL examples. Extract table names, column names, relationships, and data types exclusively from the schema. Analyze the first three rows of each table to determine column data types and sample data. Consider the provided examples to grasp the query style for each SQL statement. Use this information to craft precise SQL queries that accurately respond to the input questions. Ensure all 'Between' conditions involving dates encompass both date and time components. Refrain from referencing tables or columns beyond the provided schema. Employ aliases for clarity and ensure each column referenced in the SQL query corresponds to the table alias used.

### Database Schema and Sample Data

{table_info}

### Example NLQ-SQL Pairs

NLQ: Tell me the name of the movies of the actor CHRISTIAN AKROYD ordered by category.
SQL:
SELECT f.film_id, f.title, a.first_name, a.last_name, c.name
FROM film f
JOIN film_actor fa ON f.film_id = fa.film_id
JOIN actor a ON fa.actor_id = a.actor_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE a.first_name LIKE 'CHRISTIAN' AND a.last_name LIKE 'AKROYD'
ORDER BY c.name;

NLQ: List the total sales that Mike had in the month of June 2005. Round the value to 4 decimal places.
SQL:
SELECT s.staff_id, s.first_name, s.last_name, ROUND(SUM(p.amount), 4) AS total_sales
FROM payment p
JOIN staff s ON p.staff_id = s.staff_id
WHERE s.first_name LIKE 'Mike'
AND p.payment_date BETWEEN '2005-06-01 00:00:00' AND '2005-06-30 23:59:59'
GROUP BY s.staff_id, s.first_name, s.last_name;

NLQ: Which customers have rented more than 35 movies at store 2?
SQL:
SELECT c.customer_id, c.first_name, c.last_name, COUNT(*) AS rental_count, c.store_id
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
WHERE c.store_id = 2
GROUP BY c.customer_id
HAVING COUNT(*) > 35;

NLQ: How many movie copies are in English? Organize it by category.
SQL:
SELECT c.name, COUNT(*) AS copy_count
FROM inventory i
JOIN film f ON i.film_id = f.film_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
JOIN language l ON f.language_id = l.language_id
WHERE l.name LIKE 'English'
GROUP BY c.name;

NLQ: List all unique cities where rentals have taken place.
SQL:
SELECT DISTINCT ci.city 
FROM city ci
JOIN address a ON ci.city_id = a.city_id
JOIN customer c ON a.address_id = c.address_id
JOIN rental r ON c.customer_id = r.customer_id;

### Input Question

{nlq}

Provide only the SQL query to execute without any comments, and ensure it ends with a semicolon."""
}