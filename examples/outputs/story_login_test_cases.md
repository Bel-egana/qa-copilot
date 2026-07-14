## Coverage overview

**Nota de estrategia de cobertura para nivel Junior:** Como analista de pruebas, la estrategia de cobertura se centra en validar tanto la interfaz de usuario como la lógica del negocio descrita en los criterios de aceptación. Hemos cubierto el flujo principal (Happy Path) para asegurar que un usuario registrado pueda restablecer su contraseña con éxito, casos negativos para evitar contraseñas no seguras o el uso de enlaces vencidos, y casos de borde como la expiración exacta y el uso único del enlace. Hemos dejado fuera de forma deliberada las pruebas no funcionales, como pruebas de rendimiento bajo carga de envío de correos simultáneos, pruebas de seguridad de inyección SQL en el formulario y la compatibilidad con múltiples navegadores y dispositivos, las cuales se planificarán en una fase posterior.

---

## Gherkin scenarios

**Nota de estrategia para nivel Junior:** El objetivo de escribir escenarios en formato Gherkin (Behavior-Driven Development - BDD) es facilitar la comunicación entre el equipo de desarrollo, negocio y pruebas. Se redactan desde la perspectiva del usuario final, utilizando un lenguaje claro pero estructurado en inglés para las palabras clave (Given, When, Then) según el estándar de la industria, y el comportamiento en español.

```gherkin
Scenario: Solicitud exitosa de enlace de restablecimiento de contraseña
  Given el usuario está en la pantalla de inicio de sesión
  When hace clic en el enlace "Forgot password?"
  And ingresa un correo electrónico registrado "usuario@correo.com"
  And hace clic en el botón de enviar
  Then el sistema debe mostrar un mensaje confirmando el envío del enlace
  And el usuario debe recibir un correo con el enlace de restablecimiento

Scenario: Restablecimiento de contraseña exitoso con contraseña válida
  Given el usuario ha recibido el enlace de restablecimiento de contraseña
  And el enlace tiene menos de 24 horas de haber sido generado
  When el usuario abre el enlace
  And ingresa una nueva contraseña de "12345678" (exactamente 8 caracteres)
  And confirma la nueva contraseña
  And hace clic en guardar
  Then el sistema debe actualizar la contraseña exitosamente
  And el usuario puede iniciar sesión con su nueva contraseña

Scenario: Intento de restablecimiento de contraseña con contraseña demasiado corta
  Given el usuario ha abierto el enlace de restablecimiento válido
  When ingresa una nueva contraseña de "12345" (5 caracteres)
  And hace clic en guardar
  Then el sistema debe mostrar un mensaje de error indicando que la contraseña debe tener al menos 8 caracteres
  And la contraseña no debe ser modificada

Scenario: Intento de uso de un enlace de restablecimiento de contraseña expirado
  Given el usuario tiene un enlace de restablecimiento que fue generado hace más de 24 horas
  When el usuario intenta abrir el enlace en el navegador
  Then el sistema debe mostrar un mensaje de error indicando que el enlace ha expirado
  And no debe permitir ingresar una nueva contraseña
```

---

## Test case table

**Nota de estrategia para nivel Junior:** La matriz de casos de prueba detallada sirve como guía paso a paso para la ejecución manual del equipo de QA. Se priorizan los casos críticos (High) que impiden el flujo principal del usuario, seguidos de los de prioridad media (Medium) y baja (Low) que cubren reglas de negocio complementarias y flujos alternos. Se han documentado supuestos adicionales entre paréntesis (assumption) para clarificar el comportamiento esperado donde la historia de usuario original no especificaba el diseño del sistema.

| ID | Title | Priority | Preconditions | Steps | Expected result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| TC-001 | Visualización del enlace "Forgot password?" | High | El usuario no ha iniciado sesión y se encuentra en la pantalla de login. | 1. Navegar a la URL de inicio de sesión de la aplicación.<br>2. Verificar visualmente la presencia del enlace "Forgot password?". | El enlace "Forgot password?" es visible, está correctamente alineado y es interactivo. |
| TC-002 | Solicitud de restablecimiento con correo registrado exitosa | High | Existe un usuario registrado en el sistema con el correo usuario@test.com. | 1. Hacer clic en "Forgot password?".<br>2. Ingresar el correo usuario@test.com.<br>3. Hacer clic en el botón de enviar.<br>4. Revisar la bandeja de entrada del correo ingresado. | 1. El sistema muestra un mensaje de éxito en pantalla.<br>2. Se recibe un correo electrónico que contiene el enlace único de restablecimiento. |
| TC-003 | Solicitud de restablecimiento con correo no registrado (assumption) | Medium | El correo noexiste@test.com no está registrado en la base de datos. | 1. Hacer clic en "Forgot password?".<br>2. Ingresar el correo noexiste@test.com.<br>3. Hacer clic en el botón de enviar.<br>4. Revisar la bandeja de entrada de ese correo. | El sistema muestra un mensaje genérico de envío para evitar enumeración de usuarios (assumption)<br>2. No se recibe ningún correo de restablecimiento. |
| TC-004 | Restablecer contraseña con longitud mínima permitida (Límite - 8 caracteres) | High | El usuario ha recibido un enlace de restablecimiento válido y está dentro de las 24 horas de vigencia. | 1. Abrir el enlace recibido en el navegador.<br>2. Ingresar "Ab123456" (8 caracteres) en el campo de nueva contraseña.<br>3. Confirmar la contraseña e interactuar con el botón de guardar.<br>4. Intentar iniciar sesión con la nueva contraseña. | 1. El sistema acepta la contraseña y muestra un mensaje de éxito.<br>2. El usuario inicia sesión correctamente con la nueva contraseña "Ab123456". |
| TC-005 | Restablecer contraseña con longitud menor a la permitida (7 caracteres) | High | El usuario ha abierto un enlace de restablecimiento válido. | 1. Ingresar "Ab12345" (7 caracteres) en el campo de nueva contraseña.<br>2. Confirmar la contraseña e interactuar con el botón de guardar. | El sistema muestra un mensaje de validación indicando que la contraseña debe tener al menos 8 caracteres y no permite guardar los cambios. |
| TC-006 | Intentar usar un enlace de restablecimiento después de 24 horas (Expiración) | High | Se ha generado un enlace de restablecimiento hace exactamente 24 horas y 1 minuto. | 1. Intentar acceder a la URL del enlace de restablecimiento en el navegador. | El sistema muestra una página de error o advertencia indicando que el enlace ha expirado y no se muestra el formulario de cambio de contraseña. |
| TC-007 | Intentar usar el enlace de restablecimiento más de una vez (assumption) | Medium | El usuario ya utilizó exitosamente el enlace para cambiar su contraseña una vez. | 1. Intentar acceder nuevamente a la misma URL del enlace utilizado anteriormente. | El sistema muestra un mensaje indicando que el enlace ya no es válido o ya fue utilizado (assumption), impidiendo un segundo cambio. |