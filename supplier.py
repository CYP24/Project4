from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ims.db")


class supplierClass:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x500+320+220")
        self.root.config(bg="white")
        self.root.resizable(False, False)
        self.root.focus_force()

        # ------------ variables --------------
        self.var_searchtxt = StringVar()
        self.var_sup_invoice = StringVar()
        self.var_name = StringVar()
        self.var_contact = StringVar()

        # ---------- Search Frame -------------
        Label(self.root, text="Invoice No.", bg="white", font=("goudy old style", 15)).place(x=700, y=80)

        Entry(self.root, textvariable=self.var_searchtxt, font=("goudy old style", 15), bg="lightyellow").place(x=850, y=80, width=160)

        Button(
            self.root,
            command=self.search,
            text="Search",
            font=("goudy old style", 15),
            bg="#4caf50",
            fg="white",
            cursor="hand2"
        ).place(x=980, y=79, width=100, height=28)

        # -------------- title ---------------
        Label(
            self.root,
            text="Supplier Details",
            font=("goudy old style", 20, "bold"),
            bg="#0f4d7d",
            fg="white"
        ).place(x=50, y=10, width=1000, height=40)

        # -------------- content ---------------
        Label(self.root, text="Invoice No.", font=("goudy old style", 15), bg="white").place(x=50, y=80)
        Entry(self.root, textvariable=self.var_sup_invoice, font=("goudy old style", 15), bg="lightyellow").place(x=180, y=80, width=180)

        Label(self.root, text="Name", font=("goudy old style", 15), bg="white").place(x=50, y=120)
        Entry(self.root, textvariable=self.var_name, font=("goudy old style", 15), bg="lightyellow").place(x=180, y=120, width=180)

        Label(self.root, text="Contact", font=("goudy old style", 15), bg="white").place(x=50, y=160)
        Entry(self.root, textvariable=self.var_contact, font=("goudy old style", 15), bg="lightyellow").place(x=180, y=160, width=180)

        Label(self.root, text="Description", font=("goudy old style", 15), bg="white").place(x=50, y=200)
        self.txt_desc = Text(self.root, font=("goudy old style", 15), bg="lightyellow")
        self.txt_desc.place(x=180, y=200, width=470, height=120)

        # buttons
        Button(self.root, text="Save", command=self.add, font=("goudy old style", 15), bg="#2196f3", fg="white").place(x=180, y=370, width=110, height=35)
        Button(self.root, text="Update", command=self.update, font=("goudy old style", 15), bg="#4caf50", fg="white").place(x=300, y=370, width=110, height=35)
        Button(self.root, text="Delete", command=self.delete, font=("goudy old style", 15), bg="#f44336", fg="white").place(x=420, y=370, width=110, height=35)
        Button(self.root, text="Clear", command=self.clear, font=("goudy old style", 15), bg="#607d8b", fg="white").place(x=540, y=370, width=110, height=35)

        # table
        sup_frame = Frame(self.root, bd=3, relief=RIDGE)
        sup_frame.place(x=700, y=120, width=380, height=350)

        self.SupplierTable = ttk.Treeview(
            sup_frame,
            columns=("invoice", "name", "contact", "desc")
        )

        for col in ("invoice", "name", "contact", "desc"):
            self.SupplierTable.heading(col, text=col.capitalize())

        self.SupplierTable["show"] = "headings"
        self.SupplierTable.pack(fill=BOTH, expand=1)
        self.SupplierTable.bind("<ButtonRelease-1>", self.get_data)

        self.show()

    # ---------------- helper ----------------
    def get_connection(self):
        return sqlite3.connect(database=DB_PATH)

    def validate_input(self):
        if self.var_sup_invoice.get().strip() == "":
            messagebox.showerror("Error", "Invoice is required", parent=self.root)
            return False
        return True

    def clear_table(self):
        self.SupplierTable.delete(*self.SupplierTable.get_children())

    # ---------------- CRUD ----------------
    def show(self):
        try:
            with self.get_connection() as con:
                cur = con.cursor()
                cur.execute("select * from supplier")
                rows = cur.fetchall()

            self.clear_table()
            for row in rows:
                self.SupplierTable.insert('', END, values=row)

        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def add(self):
        if not self.validate_input():
            return

        try:
            with self.get_connection() as con:
                cur = con.cursor()
                cur.execute("select * from supplier where invoice=?", (self.var_sup_invoice.get(),))
                if cur.fetchone():
                    messagebox.showerror("Error", "Invoice already exists", parent=self.root)
                    return

                cur.execute(
                    "insert into supplier(invoice,name,contact,desc) values(?,?,?,?)",
                    (
                        self.var_sup_invoice.get(),
                        self.var_name.get(),
                        self.var_contact.get(),
                        self.txt_desc.get('1.0', END).strip()
                    )
                )
                con.commit()

            messagebox.showinfo("Success", "Supplier Added Successfully", parent=self.root)
            self.clear()

        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def get_data(self, ev):
        row = self.SupplierTable.item(self.SupplierTable.focus())['values']
        if not row:
            return

        self.var_sup_invoice.set(row[0])
        self.var_name.set(row[1])
        self.var_contact.set(row[2])
        self.txt_desc.delete('1.0', END)
        self.txt_desc.insert(END, row[3])

    def update(self):
        if not self.validate_input():
            return

        try:
            with self.get_connection() as con:
                cur = con.cursor()
                cur.execute("select * from supplier where invoice=?", (self.var_sup_invoice.get(),))
                if not cur.fetchone():
                    messagebox.showerror("Error", "Invalid Invoice No.", parent=self.root)
                    return

                cur.execute(
                    "update supplier set name=?,contact=?,desc=? where invoice=?",
                    (
                        self.var_name.get(),
                        self.var_contact.get(),
                        self.txt_desc.get('1.0', END).strip(),
                        self.var_sup_invoice.get()
                    )
                )
                con.commit()

            messagebox.showinfo("Success", "Updated Successfully", parent=self.root)
            self.show()

        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def delete(self):
        if not self.validate_input():
            return

        try:
            with self.get_connection() as con:
                cur = con.cursor()
                cur.execute("select * from supplier where invoice=?", (self.var_sup_invoice.get(),))
                if not cur.fetchone():
                    messagebox.showerror("Error", "Invalid Invoice No.", parent=self.root)
                    return

                if not messagebox.askyesno("Confirm", "Delete this record?", parent=self.root):
                    return

                cur.execute("delete from supplier where invoice=?", (self.var_sup_invoice.get(),))
                con.commit()

            messagebox.showinfo("Deleted", "Supplier Deleted", parent=self.root)
            self.clear()

        except Exception as ex:
            messagebox.showerror("Error", str(ex))

    def clear(self):
        self.var_sup_invoice.set("")
        self.var_name.set("")
        self.var_contact.set("")
        self.txt_desc.delete('1.0', END)
        self.var_searchtxt.set("")
        self.show()

    def search(self):
        if self.var_searchtxt.get().strip() == "":
            messagebox.showerror("Error", "Invoice required", parent=self.root)
            return

        try:
            with self.get_connection() as con:
                cur = con.cursor()
                cur.execute("select * from supplier where invoice=?", (self.var_searchtxt.get(),))
                row = cur.fetchone()

            self.clear_table()
            if row:
                self.SupplierTable.insert('', END, values=row)
            else:
                messagebox.showerror("Error", "No record found", parent=self.root)

        except Exception as ex:
            messagebox.showerror("Error", str(ex))


if __name__ == "__main__":
    root = Tk()
    obj = supplierClass(root)
    root.mainloop()