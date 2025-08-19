from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from django.utils.dateparse import parse_date

from .models import EmpresaRecolectora, Recoleccion, Usuario

@dataclass
class RecoleccionInput:
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
    NOMBRE_EMPRESA = "Green Orgánicos"

    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora:
        empresa, _ = EmpresaRecolectora.objects.get_or_create(
            nombre=self.NOMBRE_EMPRESA,
            defaults={"direccion": "Centro logístico - Orgánicos"},
        )
        return empresa

    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion:
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
    NOMBRE_EMPRESA = "Green Inorgánicos"

    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora:
        empresa, _ = EmpresaRecolectora.objects.get_or_create(
            nombre=self.NOMBRE_EMPRESA,
            defaults={"direccion": "Centro logístico - Inorgánicos"},
        )
        return empresa

    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion:
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
    NOMBRE_EMPRESA = "Green Peligrosos"

    def asignar_empresa(self, entrada: RecoleccionInput) -> EmpresaRecolectora:
        empresa, _ = EmpresaRecolectora.objects.get_or_create(
            nombre=self.NOMBRE_EMPRESA,
            defaults={"direccion": "Planta especializada - Peligrosos"},
        )
        return empresa

    def crear_recoleccion(self, entrada: RecoleccionInput) -> Recoleccion:
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
    @staticmethod
    def for_tipo(tipo_residuo: str) -> RecoleccionService:
        """
        Devuelve el servicio correcto según el tipo de residuo:
        O = Orgánico, I = Inorgánico, P = Peligroso
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
