# from utils.auth import split_full_name  # Comentado - no se usa sin Google login
import pyrebase
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from config.permissions import PermissionManager

# Configuración de Firebase usando variables de entorno
from config.settings import settings
from constants.role import RoleManager
from database import engine
from models_db import Person, Role, User, UserRole
from schemas.user import SignUpSchema

firebaseConfig = settings.get_firebase_web_config()

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()


def create_user_service(user_data: SignUpSchema):
    """
    Servicio para crear un usuario en Firebase y en la base de datos local.
    """
    print(f"Creating account for: {user_data}")
    # 1. Verificar primero en la base local - buscar por email en User
    with Session(engine) as session:
        existing_user = session.query(User).filter_by(email=user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User already exists in local DB"
            )

    # 2. Crear usuario en Firebase
    try:
        firebase_user = auth.create_user_with_email_and_password(
            user_data.email, user_data.password
        )
        print("Firebase localId:", firebase_user["localId"])
    except Exception as e:
        print("Error al crear usuario en Firebase:", e)
        # Si el error es de email ya registrado en Firebase
        if "EMAIL_EXISTS" in str(e):
            raise HTTPException(
                status_code=400, detail="User already exists in Firebase"
            )
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Guardar usuario en base de datos local
    try:
        with Session(engine) as session:
            print("Storing user in local DB...")
            db_person = Person(
                name=user_data.name,
                last_name=user_data.last_name,
                document_type=user_data.document_type,
                document_number=user_data.document_number,
            )
            session.add(db_person)
            session.flush()  # Para obtener el ID de la persona

            db_user = User(
                uid=firebase_user["localId"],
                email=user_data.email,
                person_id=db_person.id,
                firebase_uid=firebase_user["localId"],
            )
            session.add(db_user)
            session.flush()

            db_user_role = UserRole(
                user_id=db_user.id,
                role_id=RoleManager.get_default_role_uuid(),
            )
            session.add(db_user_role)
            session.commit()
            session.refresh(db_user)
            return {
                "message": "User created successfully",
                "user_id": str(db_user.id),
            }
    except Exception as e:
        print("Error al guardar usuario en base local, eliminando de Firebase:", e)
        # Intentar eliminar el usuario de Firebase para evitar inconsistencia
        try:
            firebase_admin = firebase.auth()
            firebase_admin.delete_user(firebase_user["localId"])
        except Exception as del_e:
            print("Error eliminando usuario de Firebase:", del_e)
        raise HTTPException(
            status_code=400,
            detail="Error saving user in DB. User removed from Firebase. " + str(e),
        )


# COMENTADO - Login con Google (no se usará por ahora)
# def google_login_service(token: str):
#     """
#     Servicio para manejar login con Google usando Firebase.
#     """
#     print("Google login attempt...")
#     print("Received token:", token)
#     try:
#         decoded_token = admin_auth.verify_id_token(token)
#         email = decoded_token.get("email")
#         full_name = decoded_token.get("name", "")
#         first_name, second_first_name, last_name, second_last_name = split_full_name(full_name)
#
#         print("Decoded token:", decoded_token)
#         print(f"Email: {email}, First Name: {first_name}, Last Name: {last_name}")
#
#         with Session(engine) as session:
#             user = session.query(User).filter_by(email=email).first()
#             if not user:
#                 # Crear usuario si no existe
#                 user = User(
#                     first_name=first_name,
#                     second_first_name=second_first_name,
#                     last_name=last_name,
#                     second_last_name=second_last_name,
#                     email=email,
#                     uid=decoded_token.get("uid"),
#                     role="USER"
#                 )
#                 session.add(user)
#                 session.commit()
#                 session.refresh(user)
#
#             return {
#                 "id": str(user.id),
#                 "email": user.email,
#                 "first_name": user.first_name,
#                 "last_name": user.last_name,
#                 "role": user.role
#             }
#     except Exception as e:
#         print("Error:", e)
#         raise HTTPException(status_code=401, detail="Token inválido")


def get_users_service():
    """
    Servicio para obtener todos los usuarios con sus datos de persona.
    """
    with Session(engine) as session:
        users = session.query(User).join(Person).all()
        return users


def get_user_by_id_service(user_id: str):
    """
    Servicio para obtener un usuario por ID con sus datos de persona.
    """
    with Session(engine) as session:
        user = session.query(User).join(Person).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


def update_user_service(user_id: str, user_data: dict):
    """
    Servicio para actualizar un usuario y sus datos de persona.
    """
    with Session(engine) as session:
        user = session.query(User).join(Person).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Actualizar campos del usuario (el email está en Person, no en User)
        if "email" in user_data and user_data["email"] is not None:
            # Obtener la persona asociada al usuario
            person = session.query(Person).filter(Person.id == user.person_id).first()
            if person:
                person.email = user_data["email"]

        # Actualizar campos de la persona
        if "person" in user_data and user_data["person"] is not None:
            person_data = user_data["person"]
            for field, value in person_data.items():
                if value is not None and hasattr(user.person, field):
                    setattr(user.person, field, value)

        session.commit()
        session.refresh(user)
        return user


def login_service(email: str, password: str):
    """
    Servicio para login con email y contraseña que incluye permisos.
    """
    print("Attempting login...")
    try:
        # Login en Firebase
        firebase_user = auth.sign_in_with_email_and_password(email, password)

        # Obtener usuario de la base de datos con eager loading de la persona
        with Session(engine) as session:
            print(f"Buscando usuario con email: {email}")
            try:
                user = (
                    session.query(User)
                    .options(selectinload(User.person))
                    .filter(User.email == email)
                    .first()
                )
                print(f"Usuario encontrado: {user}")
            except Exception as e:
                print(f"Error en consulta de base de datos: {e}")
                raise HTTPException(status_code=400, detail="Database query error")

            if user:
                print(f"Usuario ID: {user.id}, Person ID: {user.person_id}")
                # Obtener roles
                print("Obteniendo roles del usuario...")
                user_roles = session.query(UserRole).filter_by(user_id=user.id).all()
                print(f"Roles encontrados: {len(user_roles)}")
                roles = []

                for user_role in user_roles:
                    role = session.query(Role).filter_by(id=user_role.role_id).first()
                    if role:
                        role_enum = RoleManager.get_role(role.id)
                        if role_enum:
                            roles.append(role_enum)

                print(f"Roles procesados: {roles}")
                # Calcular permisos combinados
                print("Calculando permisos...")
                all_permissions = {}
                for role in roles:
                    role_permissions = PermissionManager.get_user_permissions(role)
                    # Combinar permisos (tomar el más alto)
                    for entity, actions in role_permissions.items():
                        if entity not in all_permissions:
                            all_permissions[entity] = {}
                        for action, level in actions.items():
                            current_level = all_permissions[entity].get(action, "NONE")
                            # Jerarquía: ALL > CONDITIONAL > OWN > NONE
                            if level == "ALL":
                                all_permissions[entity][action] = level
                            elif level == "CONDITIONAL" and current_level != "ALL":
                                all_permissions[entity][action] = level
                            elif level == "OWN" and current_level in [
                                "NONE",
                                "OWN",
                            ]:
                                all_permissions[entity][action] = level

                print("Preparando respuesta...")
                print(f"User person: {user.person}")
                print(f"User email: {user.email}")
                return {
                    "message": "Login successful",
                    "idToken": firebase_user["idToken"],
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "name": user.person.name,
                        "last_name": user.person.last_name,
                        "document_type": user.person.document_type,
                        "document_number": user.person.document_number,
                        "roles": [role.value for role in roles],
                        "permissions": all_permissions,
                    },
                }

        print(f"Usuario no encontrado en base de datos local para email: {email}")
        return {
            "message": "Login successful",
            "idToken": firebase_user["idToken"],
        }
    except Exception as e:
        print(f"Error en login_service: {str(e)}")
        print(f"Tipo de error: {type(e).__name__}")
        import traceback

        print(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
