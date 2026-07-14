## Summary
Esta historia de usuario busca permitir que los usuarios de la plataforma puedan guardar productos en un carrito de compras digital. El objetivo final es facilitarles el proceso de compra, permitiéndoles agrupar los artículos de su interés para adquirirlos en un momento posterior.

## Acceptance criteria
Al analizar estrictamente el texto de la historia proporcionada, **no se menciona ningún criterio de aceptación de forma explícita**. 

La historia es completamente silenciosa en cuanto a las reglas de negocio. Para que alguien que se inicia en QA entienda la importancia de esto: los criterios de aceptación son las "reglas del juego" (por ejemplo, qué pasa si agregas un producto sin stock, si hay un límite de artículos o cómo se visualiza el carrito). Al no existir en este texto, no tenemos ninguna regla para validar si el desarrollo funciona como el negocio lo requiere.

## INVEST assessment

A continuación, evaluamos la historia de usuario utilizando el método **INVEST**, una herramienta que nos ayuda a medir la calidad de una historia antes de que el equipo comience a trabajar en ella.

| Criterion | Verdict | Justification |
| :--- | :---: | :--- |
| **Independent** (Independiente) | ⚠️ | **Parcialmente comprometido.** Aunque la idea de "agregar al carrito" es un concepto claro, no sabemos si depende de que otras historias (como el catálogo de productos o el inicio de sesión) estén terminadas primero. En QA, preferimos historias que se puedan probar por separado para no retrasar las pruebas. |
| **Negotiable** (Negociable) | ✅ | **Cumple.** La historia es tan abierta que permite que el equipo de desarrollo, diseño y QA colaboren con el Dueño del Producto (PO) para definir los detalles de cómo se implementará. |
| **Valuable** (Valiosa) | ✅ | **Cumple.** Tiene un valor claro para el usuario final (poder comprar después), lo cual justifica que el equipo dedique tiempo a construir esta funcionalidad. |
| **Estimable** (Estimable) | ❌ | **No cumple.** Como junior, debes saber que los desarrolladores necesitan detalles para calcular cuánto tiempo tardarán. Al no tener reglas claras (¿el carrito se guarda en la base de datos?, ¿se necesitan animaciones visuales?), es imposible dar una estimación realista del esfuerzo. |
| **Small** (Pequeña) | ⚠️ | **Incierto.** "Agregar productos al carrito" puede sonar simple, pero si incluye lógica compleja (como validar inventario en tiempo real o manejar múltiples divisas), puede convertirse en un trabajo gigante. Sin detalles, no podemos asegurar que quepa dentro de un ciclo de trabajo (Sprint). |
| **Testable** (Probable) | ❌ | **No cumple.** Este es nuestro mayor problema en QA. No podemos diseñar pruebas porque no hay resultados esperados definidos. No sabemos qué debe pasar en la pantalla cuando el usuario hace clic en "Agregar", por lo que no sabríamos si un resultado es un error (bug) o un comportamiento correcto. |

## Testability verdict
**No, el equipo de QA no puede comenzar a diseñar pruebas con la historia tal como está escrita.** El principal y único bloqueador es la **ausencia absoluta de criterios de aceptación y especificaciones técnicas**. Sin definir reglas básicas (como el límite de cantidad por producto, el comportamiento visual del carrito, o qué ocurre si el usuario no ha iniciado sesión), cualquier caso de prueba que escribamos hoy sería pura suposición, lo cual generaría retrabajo y reportes de errores inválidos cuando el desarrollo esté listo.