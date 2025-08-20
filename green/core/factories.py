from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from django.utils.dateparse import parse_date

from .models import EmpresaRecolectora, Recoleccion, Usuario

@dataclass
class RecoleccionInput:
    """
    Estructura de entrada para crear una recolección.
    Atributos:
        tipo_residuo (str): Código del tipo de residuo ('O', 'I', 'P').
        subcategoria (str): Código de subcategoría ('OR', 'VE', 'PO').
        direccion (str): Dirección de recolección.
        fecha_estimada (str): Fecha estimada en formato 'YYYY-MM-DD'.
        cantidad_kg (str | None): Cantidad estimada en kilogramos.
        modalidad (str): Modalidad de recolección ('PR', 'BD').
        comentario (str | None): Comentarios adicionales.
        usuario (Usuario): Usuario solicitante.
    """
    tipo_residuo: str          # 'O' | 'I' | 'P'
    subcategoria: str          # 'OR' | 'VE' | 'PO'
    direccion: str
    fecha_estimada: str        # 'YYYY-MM-DD'
    cantidad_kg: str | None
    modalidad: str             # 'PR' | 'BD'
    comentario: str | None
    usuario: Usuario

class RecoleccionService(Protocol):
    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora: ...
    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion: ...

class OrganicoService:
    """
    Servicio para gestionar recolecciones de residuos orgánicos.
    """
    NOMBRE_EMPRESA = "Green Orgánicos"

    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora:
        """
        Asigna la empresa recolectora de orgánicos.
        Args:
            entrada (RecoleccionInput): Datos de la recolección.
        Returns:
            EmpresaRecolectora: Empresa asignada.
        """
        empresa, _ = EmpresaRecolectora.objects.get_or_create(
            nombre=self.NOMBRE_EMPRESA,
            defaults={"direccion": "Centro logístico - Orgánicos"},
        )
        return empresa

    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion:
        """
        Crea una recolección de orgánicos.
        Args:
            entrada (RecoleccionInput): Datos de la recolección.
        Returns:
            Recoleccion: Objeto de recolección creado.
        """
        empresa = self.asignar_empresa(entrada)
        return Recoleccion.objects.create(
            tipo_residuo=entrada.tipo_residuo,
            subcategoria=entrada.subcategoria,
            direccion=entrada.direccion.strip(),
            fecha_estimada=parse_date(entrada.fecha_estimada),
            cantidad_kg=(entrada.cantidad_kg or 0) or 0,
            modalidad_recoleccion=entrada.modalidad,
            comentario=(entrada.comentario or "").strip(),
            usuario=entrada.usuario,
            empresa=empresa,
        )

class InorganicoService:
    """
    Servicio para gestionar recolecciones de residuos inorgánicos.
    """
    NOMBRE_EMPRESA = "Green Inorgánicos"

    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora:
        """
        Asigna la empresa recolectora de inorgánicos.
        Args:
            entrada (RecoleccionInput): Datos de la recolección.
        Returns:
            EmpresaRecolectora: Empresa asignada.
        """
        empresa, _ = EmpresaRecolectora.objects.get_or_create(
            nombre=self.NOMBRE_EMPRESA,
            defaults={"direccion": "Centro logístico - Inorgánicos"},
        )
        return empresa

    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion:
        """
        Crea una recolección de inorgánicos.
        Args:
            entrada (RecoleccionInput): Datos de la recolección.
        Returns:
            Recoleccion: Objeto de recolección creado.
        """
        empresa = self.asignar_empresa(entrada)
        return Recoleccion.objects.create(
            tipo_residuo=entrada.tipo_residuo,
            subcategoria=entrada.subcategoria,
            direccion=entrada.direccion.strip(),
            fecha_estimada=parse_date(entrada.fecha_estimada),
            cantidad_kg=(entrada.cantidad_kg or 0) or 0,
            modalidad_recoleccion=entrada.modalidad,
            comentario=(entrada.comentario or "").strip(),
            usuario=entrada.usuario,
            empresa=empresa,
        )

class PeligrosoService:
    """
    Servicio para gestionar recolecciones de residuos peligrosos.
    """
    NOMBRE_EMPRESA = "Green Peligrosos"

    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora:
        """
        Asigna la empresa recolectora de peligrosos.
        Args:
            entrada (RecoleccionInput): Datos de la recolección.
        Returns:
            EmpresaRecolectora: Empresa asignada.
        """
        empresa, _ = EmpresaRecolectora.objects.get_or_create(
            nombre=self.NOMBRE_EMPRESA,
            defaults={"direccion": "Planta especializada - Peligrosos"},
        )
        return empresa

    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion:
        """
        Crea una recolección de peligrosos.
        Args:
            entrada (RecoleccionInput): Datos de la recolección.
        Returns:
            Recoleccion: Objeto de recolección creado.
        """
        empresa = self.asignar_empresa(entrada)
        return Recoleccion.objects.create(
            tipo_residuo=entrada.tipo_residuo,
            subcategoria=entrada.subcategoria,
            direccion=entrada.direccion.strip(),
            fecha_estimada=parse_date(entrada.fecha_estimada),
            cantidad_kg=(entrada.cantidad_kg or 0) or 0,
            modalidad_recoleccion=entrada.modalidad,
            comentario=(entrada.comentario or "").strip(),
            usuario=entrada.usuario,
            empresa=empresa,
        )

class RecoleccionFactory:
    """
    Fábrica para obtener el servicio adecuado según el tipo de residuo.
    """
    @staticmethod
    def for_tipo(tipo_residuo: str) -> RecoleccionService:
        """
        Devuelve el servicio correcto según el tipo de residuo.
        Args:
            tipo_residuo (str): Código del tipo de residuo ('O', 'I', 'P').
        Returns:
            RecoleccionService: Servicio correspondiente al tipo de residuo.
        Raises:
            ValueError: Si el tipo de residuo no es soportado.
        """
        mapa = {
            "O": OrganicoService(),
            "I": InorganicoService(),
            "P": PeligrosoService(),
        }
        try:
            return mapa[tipo_residuo]
        except KeyError:
            raise ValueError(f"Tipo de residuo no soportado: {tipo_residuo}")
