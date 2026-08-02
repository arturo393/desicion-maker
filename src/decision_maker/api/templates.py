TEMPLATES = {
    "car_purchase": {
        "name": "Compra de Vehículo",
        "description": "Comparación de autos usando distribución normal y triangular",
        "factors": [
            {"name": "Costo Inicial", "weight": 0.4, "maximize": False, "category": "Financiero"},
            {"name": "Mantenimiento Anual", "weight": 0.2, "maximize": False, "category": "Financiero"},
            {"name": "Reventa Futura", "weight": 0.2, "maximize": True, "category": "Financiero"},
            {"name": "Impacto Ambiental", "weight": 0.2, "maximize": True, "category": "Social"}
        ],
        "options": [
            {
                "name": "Eléctrico Puro",
                "description": "Cero emisiones",
                "variables": {
                    "Costo Inicial": {"distribution": "normal", "params": [45000, 2000]},
                    "Mantenimiento Anual": {"distribution": "triangular", "params": [300, 500, 800]},
                    "Reventa Futura": {"distribution": "normal", "params": [25000, 3000]},
                    "Impacto Ambiental": {"distribution": "normal", "params": [95, 2]}
                }
            },
            {
                "name": "Combustión",
                "description": "Económico a corto plazo",
                "variables": {
                    "Costo Inicial": {"distribution": "normal", "params": [28000, 1500]},
                    "Mantenimiento Anual": {"distribution": "normal", "params": [1000, 300]},
                    "Reventa Futura": {"distribution": "normal", "params": [12000, 2000]},
                    "Impacto Ambiental": {"distribution": "normal", "params": [40, 5]}
                }
            }
        ]
    },
    "hiring": {
        "name": "Contratación de Ejecutivo",
        "description": "Selección de candidato con incertidumbre en rendimiento",
        "factors": [
            {"name": "Experiencia Técnica", "weight": 0.35, "maximize": True, "category": "Técnico"},
            {"name": "Liderazgo", "weight": 0.25, "maximize": True, "category": "Soft Skills"},
            {"name": "Expectativa Salarial", "weight": 0.3, "maximize": False, "category": "Financiero"},
            {"name": "Riesgo de Fuga", "weight": 0.1, "maximize": False, "category": "Riesgo"}
        ],
        "options": [
            {
                "name": "Candidato A (Estrella)",
                "description": "Alto rendimiento pero caro",
                "variables": {
                    "Experiencia Técnica": {"distribution": "normal", "params": [9.5, 0.5]},
                    "Liderazgo": {"distribution": "normal", "params": [8.0, 1.0]},
                    "Expectativa Salarial": {"distribution": "normal", "params": [120000, 10000]},
                    "Riesgo de Fuga": {"distribution": "triangular", "params": [0.1, 0.4, 0.7]}
                }
            },
            {
                "name": "Candidato B (Seguro)",
                "description": "Buen balance general",
                "variables": {
                    "Experiencia Técnica": {"distribution": "normal", "params": [7.5, 0.8]},
                    "Liderazgo": {"distribution": "normal", "params": [8.5, 0.5]},
                    "Expectativa Salarial": {"distribution": "normal", "params": [90000, 5000]},
                    "Riesgo de Fuga": {"distribution": "normal", "params": [0.2, 0.1]}
                }
            }
        ]
    }
}
