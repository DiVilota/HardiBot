import hashlib
from collections import OrderedDict


class CacheLLM:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _hash(self, prompt: str, modelo: str) -> str:
        raw = f"{prompt}|{modelo}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:16]

    def guardar(self, prompt: str, modelo: str, respuesta: str):
        clave = self._hash(prompt, modelo)
        if clave in self._cache:
            self._cache.move_to_end(clave)
        else:
            if len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
        self._cache[clave] = respuesta

    def obtener(self, prompt: str, modelo: str):
        clave = self._hash(prompt, modelo)
        if clave in self._cache:
            self._hits += 1
            self._cache.move_to_end(clave)
            return self._cache[clave]
        self._misses += 1
        return None

    def estadisticas(self) -> dict:
        total = self._hits + self._misses
        tasa = (self._hits / total * 100) if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "tasa_acierto": round(tasa, 2),
            "tamano": len(self._cache),
        }

    def limpiar(self):
        self._cache.clear()
        self._hits = 0
        self._misses = 0
