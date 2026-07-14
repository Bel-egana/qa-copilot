## Coverage overview

**Nota de estrategia de cobertura (Nivel Junior):** Al analizar la historia de usuario, nos enfocamos en validar el flujo principal que genera valor al negocio (agregar productos). Dado que la historia es muy vaga, hemos definido suposiciones lógicas para el comportamiento del sistema (como la existencia de un botón, mensajes de confirmación y stock limitado). Hemos cubierto el camino feliz (agregar un producto disponible), casos negativos (productos sin stock o cantidades inválidas) y casos límite (límites de cantidad y duplicación). Hemos dejado fuera deliberadamente las pruebas no funcionales, como el rendimiento de la carga del carrito bajo estrés, la seguridad en la sesión del usuario y la compatibilidad con diferentes navegadores, para centrarnos primero en la estabilidad funcional.

---

## Gherkin scenarios

**Nota de Gherkin (Nivel Junior):** Utilizamos el formato Given-When-Then para describir el comportamiento esperado del sistema desde la perspectiva del usuario. Esto facilita la automatización del software y alinea el entendimiento entre desarrollo, QA y negocio. Dado que la historia no detalla la interfaz, asumimos la existencia de una página de detalles del producto, un botón de acción y un contador visual en el carrito de compras.

```gherkin
Scenario: Agregar un producto disponible al carrito exitosamente
  Given el usuario está en la página de detalle de un producto disponible (assumption)
  And el carrito de compras del usuario está vacío
  When el usuario hace clic en el botón "Agregar al carrito"
  Then el sistema debe mostrar un mensaje de éxito "Producto agregado" (assumption)
  And el contador del carrito en la cabecera debe actualizarse a "1" (assumption)

Scenario: Intentar agregar un producto que no tiene stock disponible
  Given el usuario está en la página de detalle de un producto sin stock disponible (assumption)
  When el usuario visualiza la página de detalle del producto
  Then el botón "Agregar al carrito" debe aparecer deshabilitado (assumption)
  And no se debe permitir la modificación de la cantidad del producto

Scenario: Incrementar la cantidad de un producto ya existente en el carrito
  Given el usuario ya tiene 1 unidad de un producto en el carrito (assumption)
  And el usuario se encuentra nuevamente en la página de detalle de ese mismo producto
  When el usuario hace clic en el botón "Agregar al carrito"
  Then la cantidad de ese producto en el carrito debe actualizarse a 2 (assumption)
  And el contador total del carrito debe actualizarse a "2"
```

---

## Test case table

**Nota de diseño de casos de prueba (Nivel Junior):** Esta tabla traduce los escenarios de alto nivel en pasos de ejecución manuales y detallados. Es fundamental que los pasos sean claros y secuenciales para que cualquier analista pueda ejecutarlos. Hemos incluido una columna de "Prioridad" para priorizar las ejecuciones cuando el tiempo sea limitado, y hemos documentado claramente las precondiciones y las suposiciones de negocio que adoptamos debido a la ambigüedad de la historia original.

| ID | Title | Priority | Preconditions | Steps | Expected result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TC-001 | Agregar un único producto disponible al carrito | High | El usuario ha iniciado sesión en el sistema (assumption).<br>El carrito de compras está vacío.<br>El producto "Camiseta Azul" tiene stock de 10 unidades. | 1. Navegar a la página de detalle del producto "Camiseta Azul".<br>2. Hacer clic en el botón "Agregar al carrito".<br>3. Verificar visualmente el icono del carrito en la esquina superior derecha.<br>4. Hacer clic en el icono del carrito para abrir la vista detallada. | El sistema muestra un mensaje flotante de confirmación "Producto agregado al carrito" (assumption).<br>El icono del carrito muestra el contador "1" (assumption).<br>En la vista del carrito se muestra el producto "Camiseta Azul" con cantidad "1". |
| TC-002 | Intentar agregar un producto agotado (sin stock) | Medium | El usuario está en la tienda en línea.<br>El producto "Zapatos Rojos" tiene stock de 0 unidades. | 1. Buscar y seleccionar el producto "Zapatos Rojos" para abrir su detalle.<br>2. Intentar hacer clic en el botón "Agregar al carrito". | El botón "Agregar al carrito" se muestra en color gris y está deshabilitado.<br>No es posible hacer clic en él.<br>El contador del carrito se mantiene sin cambios en "0". |
| TC-003 | Agregar el mismo producto varias veces para incrementar la cantidad | Medium | El usuario ya tiene "1" unidad de "Camiseta Azul" en su carrito (assumption). | 1. Navegar nuevamente al detalle del producto "Camiseta Azul".<br>2. Hacer clic en el botón "Agregar al carrito".<br>3. Abrir la vista detallada del carrito de compras. | El carrito no duplica la fila del producto.<br>La fila de "Camiseta Azul" muestra ahora cantidad "2" y el subtotal calculado correctamente en base al precio unitario (assumption). |
| TC-004 | Intentar agregar una cantidad no permitida (cero o negativa) | High | El usuario está en la página de detalle del producto "Gorra Negra".<br>La página permite editar la cantidad mediante un campo numérico (assumption). | 1. Escribir "-5" en el campo de cantidad.<br>2. Intentar hacer clic en "Agregar al carrito".<br>3. Escribir "0" en el campo de cantidad.<br>4. Intentar hacer clic en "Agregar al carrito". | El botón se deshabilita de inmediato o el sistema muestra un mensaje de error indicando "La cantidad debe ser mayor que 0" (assumption).<br>No se realiza la acción de agregar al carrito. |
| TC-005 | Validar el límite máximo de unidades permitidas para un mismo producto | Low | El límite máximo permitido por transacción es de 99 unidades por producto (assumption).<br>El usuario ya tiene 98 unidades de "Gorra Negra" en el carrito. | 1. Navegar a la página de detalle de "Gorra Negra".<br>2. Seleccionar cantidad "2" en el selector.<br>3. Hacer clic en "Agregar al carrito". | El sistema muestra una alerta emergente indicando "No puedes agregar más de 99 unidades de este producto" (assumption).<br>La cantidad en el carrito permanece en 98 unidades. |