import os
from datetime import date
from app import create_app
from app.extensions import db, bcrypt
from app.models import Socio, Estado

app = create_app()

# Mora: si el valor es > 0 en el CSV → "moroso", si es 0 → "al_dia"
def mora(val):
    return 'moroso' if int(val) > 0 else 'al_dia'

SOCIOS_DATA = [
    #  cedula,          nro,   nombres,              apellidos,             situacion,      trabajo,          agencia,          nacimiento,      sexo, cc,    sol,   ape,   cred,  cabal, visa
    ("4.123.456-7",  "1001", "Carlos Alberto",   "González Méndez",   "activo",    "Contador",         "Agencia Centro", "1985-03-15", "M", 0,     0,     0,     0,     0,     0),
    ("5.234.567-8",  "1002", "María Fernanda",   "Silva Ramírez",     "activo",    "Ingeniera",        "Agencia Norte",  "1990-07-22", "F", 15000, 0,     0,     0,     0,     0),
    ("3.345.678-9",  "1003", "Juan Pablo",       "Martínez López",    "inactivo",  "Comerciante",      "Agencia Sur",    "1978-11-03", "M", 0,     0,     0,     25000, 12000, 0),
    ("6.456.789-0",  "1004", "Ana Lucía",        "Rodríguez Pereira", "activo",    "Doctora",          "Agencia Este",   "1988-05-30", "F", 0,     0,     0,     0,     0,     0),
    ("2.567.890-1",  "1005", "Pedro Antonio",    "Flores Torres",     "jubilado",  "Docente",          "Agencia Centro", "1960-09-12", "M", 0,     5000,  0,     0,     0,     0),
    ("7.678.901-2",  "1006", "Laura Elena",      "Díaz Gutiérrez",    "activo",    "Abogada",          "Agencia Norte",  "1992-01-18", "F", 0,     0,     0,     18000, 0,     9000),
    ("8.789.012-3",  "1007", "Roberto Carlos",   "Núñez Castillo",    "activo",    "Arquitecto",       "Agencia Oeste",  "1983-08-25", "M", 0,     0,     0,     0,     0,     0),
    ("1.890.123-4",  "1008", "Carolina Beatriz", "Vargas Herrera",    "activo",    "Veterinaria",      "Agencia Sur",    "1995-04-11", "F", 0,     0,     35000, 0,     0,     0),
    ("9.901.234-5",  "1009", "Miguel Ángel",     "Soto Rojas",        "activo",    "Programador",      "Agencia Este",   "1991-12-07", "M", 0,     0,     0,     0,     0,     0),
    ("4.012.345-6",  "1010", "Patricia Andrea",  "Morales Acuña",     "inactivo",  "Administrativa",   "Agencia Centro", "1980-06-19", "F", 0,     22000, 0,     10000, 0,     0),
    ("5.123.456-7",  "1011", "Gabriel Ignacio",  "Rojas Valdés",      "activo",    "Electricista",     "Agencia Norte",  "1987-02-28", "M", 0,     0,     0,     0,     0,     0),
    ("6.234.567-8",  "1012", "Daniela Paz",      "Contreras Muñoz",   "activo",    "Diseñadora",       "Agencia Sur",    "1993-09-14", "F", 8000,  0,     0,     0,     0,     0),
    ("7.345.678-9",  "1013", "Alejandro José",   "Guzmán Fuentes",    "activo",    "Periodista",       "Agencia Oeste",  "1984-10-05", "M", 0,     0,     0,     0,     5000,  0),
    ("2.456.789-0",  "1014", "Carmen Gloria",    "Sepúlveda Araya",   "jubilado",  "Enfermera",        "Agencia Centro", "1962-07-30", "F", 0,     0,     0,     0,     0,     15000),
    ("8.567.890-1",  "1015", "Eduardo Andrés",   "Navarro Campos",    "activo",    "Agricultor",       "Agencia Este",   "1979-04-17", "M", 0,     0,     0,     0,     0,     0),
    ("9.678.901-2",  "1016", "Isabel Margarita", "Peña Sandoval",     "activo",    "Psicóloga",        "Agencia Norte",  "1991-01-09", "F", 0,     0,     0,     0,     0,     0),
    ("1.789.012-3",  "1017", "Francisco Javier", "Vega Tapia",        "activo",    "Mecánico",         "Agencia Sur",    "1986-11-23", "M", 20000, 0,     0,     0,     0,     8000),
    ("3.890.123-4",  "1018", "Verónica Andrea",  "Bustamante Pino",   "inactivo",  "Secretaria",       "Agencia Oeste",  "1977-05-15", "F", 0,     0,     0,     0,     0,     0),
    ("5.901.234-5",  "1019", "Matías Sebastián", "Parra Leiva",       "activo",    "Chef",             "Agencia Centro", "1994-12-02", "M", 0,     0,     0,     35000, 0,     0),
    ("6.012.345-6",  "1020", "Raquel Ester",     "Reyes Cáceres",     "activo",    "Farmacéutica",     "Agencia Norte",  "1989-08-08", "F", 0,     18000, 0,     0,     0,     0),
    ("7.123.456-7",  "1021", "Cristián Alonso",  "Pizarro Saavedra",  "activo",    "Bombero",          "Agencia Este",   "1990-03-21", "M", 0,     0,     0,     0,     0,     0),
    ("8.234.567-8",  "1022", "Claudia Andrea",   "Castro Morales",    "inactivo",  "Contadora",        "Agencia Sur",    "1982-06-04", "F", 0,     0,     0,     0,     0,     0),
    ("4.345.678-9",  "1023", "Ricardo Andrés",   "Salinas Ortiz",     "activo",    "Ingeniero",        "Agencia Oeste",  "1975-09-18", "M", 0,     0,     0,     0,     11000, 0),
    ("9.456.789-0",  "1024", "Francisca Javiera","Sanhueza Gallardo",  "activo",    "Dentista",         "Agencia Centro", "1996-11-27", "F", 0,     0,     0,     0,     0,     0),
    ("2.567.890-1",  "1025", "Alberto Luis",     "Figueroa Espinoza", "jubilado",  "Militar",          "Agencia Norte",  "1958-01-13", "M", 12000, 0,     0,     0,     0,     20000),
    ("6.678.901-2",  "1026", "Paula Andrea",     "Jara Venegas",      "activo",    "Profesora",        "Agencia Sur",    "1985-07-29", "F", 0,     0,     0,     0,     0,     0),
    ("8.789.012-3",  "1027", "Sergio Humberto",  "Álvarez Paredes",   "activo",    "Piloto",           "Agencia Este",   "1981-04-25", "M", 0,     0,     0,     0,     0,     0),
    ("1.890.123-4",  "1028", "Constanza Victoria","Rivera Godoy",     "activo",    "Arquitecta",       "Agencia Oeste",  "1993-02-16", "F", 0,     0,     0,     0,     7000,  0),
    ("4.901.234-5",  "1029", "Rodrigo Emilio",   "Paredes Arancibia", "activo",    "Carpintero",       "Agencia Centro", "1988-12-10", "M", 0,     0,     28000, 0,     0,     0),
    ("7.012.345-6",  "1030", "Andrea Viviana",   "Quiroga Zambrano",  "inactivo",  "Ama de casa",      "Agencia Norte",  "1983-08-05", "F", 0,     0,     0,     0,     0,     0),
    ("5.123.456-7",  "1031", "Jorge Eduardo",    "Alarcón Mancilla",  "activo",    "Taxista",          "Agencia Sur",    "1976-03-14", "M", 0,     0,     0,     0,     0,     0),
    ("3.234.567-8",  "1032", "Elisa Valentina",  "Valenzuela Caro",   "activo",    "Periodista",       "Agencia Oeste",  "1997-06-22", "F", 0,     10000, 0,     0,     0,     0),
    ("9.345.678-9",  "1033", "Víctor Manuel",    "Lizama Barraza",    "activo",    "Albañil",          "Agencia Este",   "1990-09-01", "M", 0,     0,     0,     0,     0,     0),
    ("2.456.789-0",  "1034", "Rosa Amelia",      "Palma Cifuentes",   "jubilado",  "Costurera",        "Agencia Centro", "1955-05-28", "F", 0,     0,     0,     0,     0,     0),
    ("8.567.890-1",  "1035", "Arturo Enrique",   "Saavedra Marín",    "activo",    "Gasfiter",         "Agencia Norte",  "1984-07-19", "M", 17000, 0,     0,     0,     0,     0),
    ("5.678.901-2",  "1036", "Catalina Ignacia", "Donoso Vidal",      "activo",    "Ingeniera",        "Agencia Sur",    "1992-11-11", "F", 0,     0,     0,     0,     0,     0),
    ("1.789.012-3",  "1037", "Roberto Esteban",  "Toro Riquelme",     "activo",    "Pescador",         "Agencia Oeste",  "1973-10-30", "M", 0,     0,     0,     45000, 0,     0),
    ("6.890.123-4",  "1038", "Marcela Alejandra","Poblete Cárdenas",  "inactivo",  "Estudiante",       "Agencia Este",   "2000-01-26", "F", 0,     0,     0,     0,     0,     0),
    ("4.901.234-5",  "1039", "Esteban Gabriel",  "Cuevas Henríquez",  "activo",    "Médico",           "Agencia Centro", "1979-06-07", "M", 0,     0,     0,     0,     0,     0),
    ("9.012.345-6",  "1040", "Susana Beatriz",   "Ossandón Pavez",    "activo",    "Publicista",       "Agencia Norte",  "1990-12-31", "F", 0,     0,     0,     0,     9000,  0),
    ("3.123.456-7",  "1041", "Nelson Fabián",    "Santibáñez Acosta", "activo",    "Vendedor",         "Agencia Sur",    "1987-04-12", "M", 0,     0,     0,     0,     0,     0),
    ("6.234.567-8",  "1042", "Ximena Andrea",    "Arriagada Troncoso","activo",    "Contadora",        "Agencia Oeste",  "1985-09-03", "F", 22000, 0,     0,     0,     0,     0),
    ("8.345.678-9",  "1043", "Pablo Renato",     "Fonseca Meza",      "activo",    "Auditor",          "Agencia Este",   "1991-07-21", "M", 0,     0,     0,     0,     0,     0),
    ("1.456.789-0",  "1044", "Gladys del Carmen","Lagos Barrera",     "jubilado",  "Telefonista",      "Agencia Centro", "1953-02-17", "F", 0,     0,     0,     0,     0,     0),
    ("5.567.890-1",  "1045", "Luis Felipe",      "Bravo Araya",       "activo",    "Constructor",      "Agencia Norte",  "1982-08-09", "M", 0,     0,     16000, 0,     0,     0),
    ("7.678.901-2",  "1046", "Débora Esther",    "León Hermosilla",   "activo",    "Nutricionista",    "Agencia Sur",    "1995-05-14", "F", 0,     0,     0,     0,     0,     0),
    ("9.789.012-3",  "1047", "Simón Andrés",     "Riquelme Pinto",    "activo",    "Músico",           "Agencia Oeste",  "1994-01-02", "M", 0,     0,     0,     0,     0,     6000),
    ("2.890.123-4",  "1048", "Angélica María",   "Zúñiga Delgado",    "inactivo",  "Emprendedora",     "Agencia Este",   "1980-10-18", "F", 0,     15000, 0,     0,     5000,  0),
    ("4.901.234-5",  "1049", "Oscar Daniel",     "Aravena Madrid",    "activo",    "Abogado",          "Agencia Centro", "1978-06-25", "M", 0,     0,     0,     0,     0,     0),
    ("6.012.345-6",  "1050", "Josefina Aurora",  "Hernández Millán",  "activo",    "Odontóloga",       "Agencia Norte",  "1997-04-03", "F", 0,     0,     0,     0,     0,     0),
]

def seed_socios():
    with app.app_context():
        db.create_all()
        insertados = 0
        omitidos = 0

        for row in SOCIOS_DATA:
            cedula, nro, nombres, apellidos, situacion, trabajo, agencia, nacimiento, sexo, cc, sol, ape, cred, cabal, visa = row

            # Evitar duplicados por cédula o nro_socio
            if Socio.query.filter_by(cedula=cedula).first() or Socio.query.filter_by(nro_socio=nro).first():
                print(f"  [OMITIDO] {nro} - {nombres} {apellidos} (ya existe)")
                omitidos += 1
                continue

            fecha_nac = date.fromisoformat(nacimiento)
            socio = Socio(
                cedula=cedula,
                nro_socio=nro,
                nombres=nombres,
                apellidos=apellidos,
                situacion=situacion,
                trabajo=trabajo,
                agencia=agencia,
                fecha_nacimiento=fecha_nac,
                sexo=sexo,
            )
            db.session.add(socio)
            db.session.flush()  # para obtener socio.id

            estado = Estado(
                socio_id=socio.id,
                mora_cc=mora(cc),
                mora_sol=mora(sol),
                mora_ape=mora(ape),
                mora_credito=mora(cred),
                mora_cabal=mora(cabal),
                mora_visa=mora(visa),
            )
            db.session.add(estado)
            insertados += 1
            print(f"  [OK] {nro} - {nombres} {apellidos}")

        db.session.commit()
        print(f"\nListo: {insertados} socios insertados, {omitidos} omitidos.")

if __name__ == '__main__':
    seed_socios()
