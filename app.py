"""Lista de tareas: una página web en Flask que guarda las tareas en PostgreSQL."""

import os
import socket

import psycopg
from flask import Flask, redirect, render_template, request

app = Flask(__name__)
DATABASE_URL = os.environ["DATABASE_URL"]  # dónde está la base, nos la pasa Docker


def conectar():
    return psycopg.connect(DATABASE_URL)


def crear_tabla():
    with conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id     SERIAL PRIMARY KEY,
                texto  TEXT NOT NULL,
                hecha  BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)


@app.get("/")
def inicio():
    with conectar() as con:
        tareas = con.execute("SELECT id, texto, hecha FROM tareas ORDER BY id").fetchall()
    # socket.gethostname() dentro de un contenedor es el id corto del contenedor
    return render_template("index.html", tareas=tareas, servidor=socket.gethostname())


@app.post("/agregar")
def agregar():
    texto = request.form["texto"].strip()
    if texto:
        with conectar() as con:
            con.execute("INSERT INTO tareas (texto) VALUES (%s)", (texto,))
    return redirect("/")


@app.post("/hecha/<int:id>")
def marcar(id):
    with conectar() as con:
        con.execute("UPDATE tareas SET hecha = NOT hecha WHERE id = %s", (id,))
    return redirect("/")


@app.get("/salud")
def salud():
    with conectar() as con:
        con.execute("SELECT 1")
    return {"estado": "ok"}


crear_tabla()  # al arrancar: si la tabla no existe, la crea
