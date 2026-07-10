import io
import os
import uuid


CLOUDINARY_URL = os.environ.get("CLOUDINARY_URL", "").strip()


def armazenamento_externo_ativo():
    return bool(CLOUDINARY_URL)


def salvar_imagem(arquivo, extensao, upload_folder):
    if armazenamento_externo_ativo():
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(secure=True)
        conteudo = arquivo.stream.read()
        arquivo.stream.seek(0)
        buffer = io.BytesIO(conteudo)
        buffer.name = arquivo.filename or f"imagem.{extensao}"
        resultado = cloudinary.uploader.upload(
            buffer,
            folder="mercado-colatina/anuncios",
            resource_type="image",
            unique_filename=True,
            overwrite=False,
        )
        return resultado["secure_url"], resultado["public_id"]

    nome = f"{uuid.uuid4().hex}.{extensao}"
    arquivo.save(os.path.join(upload_folder, nome))
    return nome, None


def excluir_imagem(foto, foto_id, upload_folder):
    if not foto:
        return
    if foto_id and armazenamento_externo_ativo():
        import cloudinary
        import cloudinary.uploader

        cloudinary.config(secure=True)
        cloudinary.uploader.destroy(foto_id, resource_type="image", invalidate=True)
        return
    if foto.startswith(("http://", "https://")):
        return
    caminho = os.path.join(upload_folder, foto)
    if os.path.isfile(caminho):
        os.remove(caminho)
