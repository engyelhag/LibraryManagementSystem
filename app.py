from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Helper function to interact with the database
def query_db(query, args=(), one=False):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute(query, args)
    result = cur.fetchall()
    con.commit()
    con.close()
    return (result[0] if result else None) if one else result

# Initialize the database
def init_db():
    with sqlite3.connect('database.db') as con:
        con.execute('''CREATE TABLE IF NOT EXISTS books (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL,
                        author TEXT NOT NULL,
                        quantity INTEGER NOT NULL)''')
        con.execute('''CREATE TABLE IF NOT EXISTS borrowed_books (
                        id INTEGER PRIMARY KEY,
                        book_id INTEGER,
                        borrower TEXT NOT NULL,
                        FOREIGN KEY(book_id) REFERENCES books(id))''')
    con.close()

@app.route('/')
def index():
    books = query_db("SELECT * FROM books")
    return render_template('index.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = int(request.form['quantity'])
        query_db("INSERT INTO books (title, author, quantity) VALUES (?, ?, ?)", [title, author, quantity])
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/remove', methods=['GET', 'POST'])
def remove_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        query_db("DELETE FROM books WHERE id = ?", [book_id])
        return redirect(url_for('index'))
    books = query_db("SELECT * FROM books")
    return render_template('remove_book.html', books=books)

@app.route('/borrow', methods=['GET', 'POST'])
def borrow_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        borrower = request.form['borrower']
        query_db("INSERT INTO borrowed_books (book_id, borrower) VALUES (?, ?)", [book_id, borrower])
        query_db("UPDATE books SET quantity = quantity - 1 WHERE id = ?", [book_id])
        return redirect(url_for('index'))
    books = query_db("SELECT * FROM books WHERE quantity > 0")
    return render_template('borrow_book.html', books=books)

'''@app.route('/return', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        borrower = request.form['borrower']
        query_db("DELETE FROM borrowed_books WHERE book_id = ? AND borrower = ?", [book_id, borrower])
        query_db("UPDATE books SET quantity = quantity + 1 WHERE id = ?", [book_id])
        return redirect(url_for('index'))
    books = query_db("SELECT * FROM borrowed_books")
    return render_template('return_book.html', books=books)
'''


@app.route('/return', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        book_id = int(request.form['book_id'])
        borrower = request.form['borrower']

        # Delete from borrowed_books
        query_db("DELETE FROM borrowed_books WHERE book_id = ? AND borrower = ?", [book_id, borrower])

        # Update the books table
        query_db("UPDATE books SET quantity = quantity + 1 WHERE id = ?", [book_id])

        # Redirect to refresh the list
        return redirect(url_for('return_book'))

    # Fetch currently borrowed books
    books = query_db('''SELECT borrowed_books.book_id, books.title, borrowed_books.borrower
                         FROM borrowed_books
                         JOIN books ON borrowed_books.book_id = books.id''')

    return render_template('return_book.html', books=books)


@app.route('/search', methods=['GET', 'POST'])
def search_books():
    books = []
    if request.method == 'POST':
        search_query = request.form['search_query']
        books = query_db("SELECT * FROM books WHERE title LIKE ? OR author LIKE ?",
                         [f"%{search_query}%", f"%{search_query}%"])
    return render_template('search_books.html', books=books)

@app.route('/debug')
def debug_borrowed_books():
    borrowed_books = query_db("SELECT * FROM borrowed_books")
    return {'borrowed_books': borrowed_books}


if __name__ == '__main__':
    init_db()  # Initialize database
    app.run(debug=True)
