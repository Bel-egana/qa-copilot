## Ambiguidades

*   **"As a user" (Como usuario):** No se especifica si se refiere a un usuario visitante (invitado) o a un usuario registrado que ha iniciado sesión.
    *   *Por qué importa:* El diseño técnico y la experiencia de usuario cambian drásticamente. Si es un invitado, la información del carrito se suele guardar en el navegador (Local Storage o Cookies). Si está registrado, debe persistir en la base de datos para que pueda verlo en diferentes dispositivos.
*   **"add products" (añadir productos):** No se detalla desde qué pantallas se pueden agregar los productos (¿desde la lista de productos, desde el detalle del producto, o desde ambos?). Tampoco se aclara si se añade de uno en uno o si se puede elegir una cantidad específica antes de añadir.
    *   *Por qué importa:* El equipo de desarrollo no sabrá qué componentes de la interfaz de usuario (UI) debe modificar, y el equipo de pruebas no sabrá dónde validar la funcionalidad del botón "Añadir".
*   **"buy them later" (comprarlos más tarde):** La frase implica que el carrito debe guardar el estado de los productos, pero no define cuánto tiempo es "más tarde".
    *   *Por qué importa:* Necesitamos saber si el carrito expira después de cierto tiempo de inactividad (por ejemplo, 30 días, o al cerrar la sesión) para configurar la persistencia de datos de manera correcta y no acumular registros innecesarios en la base de datos.

---

## Missing acceptance criteria

*   **Validación de stock disponible:** La historia no menciona qué sucede si un usuario intenta agregar un producto que no tiene unidades disponibles.
    *   *Por qué importa:* Si no se valida el stock en este paso, el usuario podría agregar productos agotados, lo que generará errores frustrantes y costosos en el momento de intentar realizar el pago.
*   **Límites de cantidad de productos:** No se define un límite máximo de artículos que se pueden agregar al carrito (por ejemplo, máximo 99 unidades de un mismo producto o un peso/volumen total).
    *   *Por qué importa:* Sin un límite, el sistema es vulnerable a pruebas de estrés negativas donde un usuario (o un bot) intente agregar millones de productos, lo que podría ralentizar la base de datos o colapsar la aplicación.
*   **Mensaje de confirmación (Feedback visual):** No se especifica si el usuario debe recibir una confirmación visual cuando un producto se agrega con éxito.
    *   *Por qué importa:* Si el usuario hace clic en "Añadir" y no pasa nada visible, asumirá que el sistema no funciona y hará clic repetidas veces, lo que resultará en múltiples unidades agregadas por error y una mala experiencia de usuario.
*   **Control de productos duplicados:** No se define el comportamiento cuando se agrega un producto que ya existe en el carrito.
    *   *Por qué importa:* Debemos especificar si el sistema debe agregar una nueva línea en el carrito o simplemente incrementar la cantidad del producto ya existente.

---

## Edge cases not covered

*   **Producto que se agota mientras está en el carrito:** ¿Qué ocurre si el usuario agrega un producto del cual queda 1 unidad, pero otro cliente lo compra antes de que este usuario complete su compra "más tarde"?
    *   *Por qué importa:* El sistema debe ser capaz de actualizar el estado del carrito dinámicamente y avisar al usuario que el artículo ya no está disponible para evitar errores en la pasarela de pago.
*   **Intentar agregar cantidades no válidas:** Intentar agregar 0, números negativos, letras o caracteres especiales en el campo de cantidad.
    *   *Por qué importa:* Es un escenario típico de pruebas de seguridad y robustez. Si el sistema no valida estos datos en el backend, un usuario malintencionado podría corromper la base de datos o incluso generar carritos con precios totales negativos.
*   **Sesiones concurrentes del mismo usuario:** El usuario inicia sesión en su teléfono móvil y en su ordenador al mismo tiempo, y agrega productos al carrito desde ambos dispositivos.
    *   *Por qué importa:* Si no se maneja la sincronización de la sesión en el servidor, los carritos de ambos dispositivos podrían entrar en conflicto, sobrescribirse o duplicar los productos de forma inesperada.
*   **Producto eliminado o modificado por el administrador:** El administrador de la tienda elimina un producto o cambia su precio mientras el usuario lo tiene guardado en su carrito para "más tarde".
    *   *Por qué importa:* El sistema debe validar que el producto siga existiendo y que el precio se actualice al valor real vigente antes de proceder al pago, para evitar pérdidas económicas o reclamos legales por publicidad engañosa.

---

## Questions for the Product Owner

1.  **¿El carrito de compras estará disponible para usuarios no registrados (invitados), o será obligatorio iniciar sesión para poder agregar productos?**
    *   *Razón:* Es la pregunta más crítica porque define la arquitectura del almacenamiento (Local Storage vs. Base de datos) y el flujo de navegación del usuario.
2.  **¿Qué regla de negocio debemos aplicar si el usuario intenta agregar un producto que no tiene stock suficiente? ¿Se deshabilita el botón, o se muestra un mensaje de error?**
    *   *Razón:* Define la interacción y los mensajes de error que el frontend debe implementar para manejar el inventario.
3.  **¿Los productos en el carrito tienen un tiempo de expiración (por ejemplo, se eliminan después de 7 días) o se guardan indefinidamente hasta que el usuario los compre o los elimine manualmente?**
    *   *Razón:* Vital para que los desarrolladores configuren tareas automáticas de limpieza en la base de datos y para definir las expectativas de experiencia de usuario a largo plazo.
4.  **Cuando un usuario agrega un producto que ya está en el carrito, ¿debemos sumar la cantidad al artículo existente o crear una línea nueva en el listado del carrito?**
    *   *Razón:* Define la lógica de presentación de la interfaz del carrito y evita confusiones visuales para el cliente.
5.  **¿Cuál es el límite máximo de unidades que un usuario puede agregar de un solo producto y del total del carrito?**
    *   *Razón:* Necesitamos este dato numérico exacto para programar las validaciones de límite (tanto en frontend como en backend) antes de que se inicie el desarrollo.