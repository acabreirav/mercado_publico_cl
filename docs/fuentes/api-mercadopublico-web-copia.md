# **Términos y condiciones de uso**

La Dirección ChileCompra establece las siguientes Políticas y Condiciones de Uso de la API de Mercado Público, las que se entienden aceptadas por las personas usuarias desde el momento en que hacen uso de este sistema. 

Estas Políticas y Condiciones **tienen como objetivo asegurar el uso correcto de la información disponible, ya sea para el desarrollo de aplicaciones, la descarga de datos o su publicación.** 

La API de Mercado Público es una herramienta que permite que distintos sistemas se comuniquen entre sí y accedan a funciones e información ya disponibles en la plataforma Mercado Público, así como en otras infraestructuras y aplicaciones. Este servicio se enmarca en las políticas de transparencia y datos abiertos de la Dirección ChileCompra.

# Información proporcionada

A través de la API de Mercado Público se puede acceder a información del mercado de compras públicas generada en el portal [www.mercadopublico.cl](http://www.mercadopublico.cl/). Estos datos son de carácter público, están disponibles en línea y corresponden, entre otros, a licitaciones y órdenes de compra realizadas por los organismos públicos usuarios de la plataforma. 

ChileCompra podrá incorporar nuevos tipos de datos o reemplazar los existentes. En caso de modificar la forma de entrega de la información, suspender o dejar de proporcionar algunos datos, se informará previamente a las personas usuarias.

## El acceso a esta información es gratuito para todo tipo de usuarios. No obstante, su uso requiere ciertos conocimientos técnicos y debe realizarse exclusivamente a través de los mecanismos descritos en api.mercadopublico.cl.

# Uso de la información

1\. Los niveles de servicio de la API de Mercado Público se definen conforme a los estándares establecidos por la Dirección ChileCompra.

2\. El acceso a la API se realiza mediante un ticket, el cual debe ser solicitado a través del formulario disponible, seleccionando la opción “Solicitud de Ticket”.

3\. El formulario debe ser completado con datos reales de la persona solicitante —nombre y apellido, RUT y correo electrónico—, ya que se entrega un único ticket por persona. Si la Dirección ChileCompra detecta inconsistencias en la información proporcionada, podrá limitar o suspender el acceso asociado a dicho ticket.

4\. ChileCompra utilizará estos datos personales únicamente para fines de operación, control y administración del servicio de la API de Mercado Público, y no los compartirá con terceros, salvo por mandato judicial.

5\. El funcionamiento y uso de la API es monitoreado de forma permanente por la Dirección ChileCompra, con el fin de asegurar su correcto uso y estabilidad. Este monitoreo incluye validaciones por dirección IP, pudiendo establecerse restricciones de acceso según la cantidad de solicitudes realizadas desde una misma IP.

6\. El soporte para el uso de la API debe solicitarse a través del formulario de sugerencias disponible en el sitio web. Todas las consultas y solicitudes serán respondidas en un plazo máximo de 3 días hábiles. No se considerarán solicitudes informales ni aquellas enviadas directamente a correos institucionales. No existen otros canales de soporte distintos a los señalados en estas Políticas y Condiciones.

7\. Cada ticket de acceso cuenta con un límite diario de 10.000 solicitudes. Este límite no es modificable y tiene como finalidad resguardar la estabilidad del servicio. Las personas usuarias se comprometen a no exceder ni eludir estas limitaciones. El uso excesivo o abusivo de la API podrá derivar en la suspensión temporal o el bloqueo permanente del acceso.

8\. Para procesos de alta demanda o descarga masiva de información, se recomienda realizar las consultas en horario nocturno, entre las 22:00 y las 07:00 horas.

# Límites de responsabilidad

1\. La API de Mercado Público es un servicio adicional que ChileCompra pone a disposición de manera voluntaria. Su uso no genera derechos adquiridos para las personas usuarias, por lo que ChileCompra podrá modificar, suspender o dar término al servicio cuando lo estime pertinente. 

2\. ChileCompra podrá actualizar estas Políticas y Condiciones de Uso en cualquier momento, manteniendo siempre disponible la versión vigente en el sitio web. 

3\. Esta Dirección no se hace responsable de la información publicada por las personas usuarias a través de las aplicaciones o sistemas que desarrollen utilizando la API, ni de los proyectos, actividades comerciales o cobros asociados a dichos desarrollos. 

4\. Las personas usuarias que publiquen información obtenida desde la API de Mercado Público, sin modificarla, deberán indicar claramente que la fuente de los datos es la Dirección ChileCompra. 

# **Información disponible**

# Accede a los datos en línea de licitaciones, órdenes de compra, organismos compradores y proveedores del Estado.

#### 1 [**LICITACIONES**](https://www.chilecompra.cl/api/#1769524491975-53626512-0329)

Tienes acceso a información para listar: 

* Licitaciones diarias   
* Licitaciones por código   
* Licitaciones diarias por estado   
* Licitaciones por día   
* Licitaciones por estado y día   
* Licitaciones por código de organismo público o [proveedor](https://www.chilecompra.cl/glosario/proveedor/) 

La API fue implementada para que las URLs puedan ser utilizadas mediante parámetros GET, con el objetivo de indicar las características de la petición que se ejecuta. 

## Servicios web

Los archivos de los recursos a los que se accede a través de la API utilizan las siguientes estructuras: 

* **Formato JSON:**  
  https://api.mercadopublico.cl/servicios/v1/publico/**licitaciones.json**?fecha=02022014\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844   
* **Formato JSONP:**  
  https://api.mercadopublico.cl/servicios/v1/publico/**licitaciones.jsonp**?fecha=02022014\&callback=respuesta\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844   
* **Formato XML:**  
  https://api.mercadopublico.cl/servicios/v1/publico/**licitaciones.xml**?fecha=02022014\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

**IMPORTANTE:**  
Los estados de las licitaciones consultadas se mostrarán por códigos, descritos de la siguiente forma: 

* Publicada \= “5”   
* Cerrada \= “6”   
* Desierta \= “7”   
* Adjudicada \= “8”   
* Revocada \= “18”   
* Suspendida \= “19”

## Tipos de consultas

## Por {código} de licitación

Ejemplo de {codigo} \= 1509-5-L114

[https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?codigo=1509-5-L114\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844](https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?codigo=1509-5-L114&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844) 

## Por todos los estados del día actual

[https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844](https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844)

## Por todos los estados de una {fecha} en particular

Ejemplo de {fecha} \= 02022014   
   
[https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844](https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844) 

## Por estado "activas"

La opción estados “activas”, muestra todas las licitaciones publicadas al día de realizada la consulta. 

*https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?estado=**{estado}**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*

*https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?estado=**activas**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*

## Por {estado} del día actual

{estados} de las licitaciones 

* Publicada   
* Cerrada   
* Desierta   
* Adjudicada   
* Revocada   
* Suspendida   
* Todos *(muestra todos los estados posibles antes señalados)* 

*https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014\&estado=**{estado}**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*

*https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014\&estado=**adjudicada**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844* 

## Por {código} de proveedor

Ejemplo de {CódigoProveedor} \= 17793   
   
https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014\&CodigoProveedor={CódigoProveedor}\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844   
   
https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014\&CodigoProveedor=17793\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

## Por {código} de organismo público

Ejemplo de {CódigoOrganismo} \= 694   
   
https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha={fecha}\&CodigoOrganismo={CódigoOrganismo}\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844   
   
https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json?fecha=02022014\&CodigoOrganismo=6945\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844 

Los resultados de las búsquedas son realizadas en base a las licitaciones publicadas en el día y contienen información básica de las licitaciones. 

En el caso de la búsqueda por código, no es relevante la fecha, dado que siempre se obtendrá la licitación solicitada. El resultado entregado por la búsqueda será información detallada de la licitación. 

El formato de la fecha es ddmmaaaa, ejemplo: 12062026, obtendrá las licitaciones del día 12 del mes de junio del año 2026\.

## Documentación de licitación

### [**https://api.mercadopublico.cl/modules/Licitacion.aspx**](https://api.mercadopublico.cl/modules/Licitacion.aspx)

## Es necesario revisar las tipologías de licitaciones que ya no existen

Cantidad

FechaCreacion

Version

Listado 

Cantidad de Licitaciones consultadas 

Fecha de consulta

Versión del API de Mercado Público

Listado de Licitaciones

## ANEXOS

## Tipo de licitación

### **Valor** 

[L1](https://www.chilecompra.cl/glosario/l1/)

[LE](https://www.chilecompra.cl/glosario/le/)

[LP](https://www.chilecompra.cl/glosario/lp/)

[LS](https://www.chilecompra.cl/glosario/ls/)

A1

B1

J1

F1

E1

CO

[B2](https://www.chilecompra.cl/glosario/b2/)

A2

D1

[E2](https://www.chilecompra.cl/glosario/e2/)

C2

C1

F2

F3

G2

G1

R1

CA

SE

### **Descripción**

[Licitación Pública](https://www.chilecompra.cl/glosario/licitacion-publica/) Menor a 100 UTM ([L1](https://www.chilecompra.cl/glosario/l1/))

[Licitación Pública](https://www.chilecompra.cl/glosario/licitacion-publica/) Entre 100 y 1000 UTM ([LE](https://www.chilecompra.cl/glosario/le/))

[Licitación Pública](https://www.chilecompra.cl/glosario/licitacion-publica/) Mayor 1000 UTM ([LP](https://www.chilecompra.cl/glosario/lp/))

[Licitación Pública](https://www.chilecompra.cl/glosario/licitacion-publica/) [Servicios personales](https://www.chilecompra.cl/glosario/servicios-personales/) especializados ([LS](https://www.chilecompra.cl/glosario/ls/))

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) por [Licitación Pública](https://www.chilecompra.cl/glosario/licitacion-publica/) anterior sin oferentes (A1)

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) por otras causales, excluidas de la ley de Compras

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) por Servicios de Naturaleza Confidencial

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) por Convenios con Personas Jurídicas Extranjeras fuera del Territorio Nacional

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) por Remanente de Contrato anterior

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) entre 100 y 1000 UTM

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) Mayor a 1000 UTM

[Trato Directo](https://www.chilecompra.cl/glosario/trato-directo/) por Producto de [Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) anterior sin oferentes o desierta

[Trato Directo](https://www.chilecompra.cl/glosario/trato-directo/) por [Proveedor](https://www.chilecompra.cl/glosario/proveedor/) Único (D1)

[Licitación Privada](https://www.chilecompra.cl/glosario/licitacion-privada/) Menor a 100 UTM

[Trato Directo](https://www.chilecompra.cl/glosario/trato-directo/) ([Cotización](https://www.chilecompra.cl/glosario/cotizacion/)) (C2)

Compra Directa (Orden de compra) (C1) 

[Trato Directo](https://www.chilecompra.cl/glosario/trato-directo/) ([Cotización](https://www.chilecompra.cl/glosario/cotizacion/)) (F2)

Compra Directa (Orden de compra) (F3)

Directo ([Cotización](https://www.chilecompra.cl/glosario/cotizacion/)) (G2)

Compra Directa (Orden de compra) (G1)

Orden de Compra menor a 3 UTM (R1)

Orden de Compra sin Resolución (CA)

Orden de Compra proveniente de adquisición sin emisión automática de OC (SE)

## Unidad monetaria

### **Valor** 

CLP

CLF

USD

UTM

EUR

### **Descripción**

Peso Chileno

Unidad de Fomento

Dólar Americano

Unidad Tributaria Mensual

Euro

## Monto estimado

### **Valor** 

1

2

### **Descripción**

Presupuesto Disponible 

Precio Referencial 

## Modalidad de pago

### **Valor** 

1

2

3

4

5

6

7

8

9

10

### **Descripción**

Pago a 30 días

Pago a 30, 60 y 90 días

Pago al día

Pago Anual

Pago a 60 días 

Pagos Mensuales

Pago Contra Entrega Conforme 

Pago Bimensual

Pago Por Estado de Avance

Pago Trimestral

## Unidad de Tiempo de Evaluación

### **Valor** 

1

2

3

4

5

### **Descripción**

Horas

Días

Semanas

Meses

Años

## Unidad de Tiempo duración del contrato

### **Valor** 

1

2

3

4

5

### **Descripción**

Horas

Días

Semanas

Meses

Años

## Tipo de Acto Administrativo que adjudica o aprueba el contrato

### **Valor** 

1

2

3

5

4

### **Descripción**

Autorización

Resolución

Otros

Acuerdo

Decreto

## Valores Binarios

Existen varios datos del XML de licitación que se formatean en base a lógica binaria, estos son:

### **Campo**

### **Comentario**

### **Valores**

### **Valores**

Licitación informada

Informa el tipo de Licitación

1=Si   
0=No

\<Informada\>0\</Informada\>

Tipo de Licitación

Especifica si la licitación es informada

1=Pública   
2=Privada

\<CodigoTipo\>1\</CodigoTipo\>

Toma de Razón

Indica si la Licitación requiere toma de razón por parte de la Contraloría

1=Si   
0=N0

\<TomaRazon\>0\</TomaRazon\>

Visibilidad de Ofertas técnicas

Sí, las ofertas técnicas serán de público conocimiento una vez realizada la apertura técnica de las ofertas.

1=Si   
0=No

\<EstadoPublicidadOfertas\>1\</EstadoPublicidadOfertas\>

Contrato

1=Si   
0=No

\<Contrato\>NO\</Contrato\>

Obras

Licitación del tipo Obra Pública

2=Si   
1=No

\<Obras\>0\</Obras\>

Visibilidad del Monto

Hacer público el monto estimado en la ficha de la licitación

1=Si   
0=No

\<VisibilidadMonto\>1\</VisibilidadMonto\>

Permite Subcontratación

Permite la subcontratación

1=Si   
0=No

\<SubContratacion\>1\</SubContratacion\>

Extensión del Plazo

Si a la fecha/hora de cierre de recepción de ofertas, se han recibido 2 o menos propuestas, el plazo de cierre se ampliará automáticamente en 2 días hábiles, por una sola vez, bajo las condiciones establecidas por el artículo 25, inciso final, del reglamento de la ley 19.886.

1=Extiende   
0=No extiende

\<ExtensionPlazo\>0\</ExtensionPlazo\>

Es Base Tipo

Indica si la licitación fue creada a través de licitaciones tipo.

1=Si   
0=No

\<EsBaseTipo\>0\</EsBaseTipo\>

Es Renovable

1=Si   
0=No

\<EsRenovable\>0\</EsRenovable\>

**2 Compra agil**  
**Detalles en documentos:**  
**Documentacion\_API\_Compra\_Agil-2-1.pdf y Documentacion\_API\_Compra\_Agil-3-1.pdf**

**3 Ordenes de compra**  
Tienes acceso a información para listar:

* Órdenes de compra diarias   
* Órdenes de compra por código   
* Órdenes de compra diarias por estado   
* Órdenes de compra por día   
* Órdenes de compra por estado y día   
* Órdenes de compra por código de organismo público o [proveedor](https://www.chilecompra.cl/glosario/proveedor/) 

La API fue implementada para que las URLs puedan ser utilizadas mediante parámetros GET, con el objetivo de indicar las características de la petición que se ejecuta.

## Servicio web

Los archivos de los recursos a los que se accede a través de api.mercadopublico.cl, utilizan las siguientes estructuras: 

* **Formato JSON:**   
  https://api.mercadopublico.cl/servicios/v1/publico/**ordenesdecompra.json**?fecha=02022014\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844   
* **Formato JSONP:**   
  https://api.mercadopublico.cl/servicios/v1/publico/**ordenesdecompra.jsonp**?fecha=02022014\&callback=respuesta\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844   
* **Formato XML:**   
  https://api.mercadopublico.cl/servicios/v1/publico/**ordenesdecompra.xml**?fecha=02022014\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844 

## IMPORTANTE

Los estados de las órdenes de compra consultadas serán mostrados por código, descritos de la siguiente forma: 

* Enviada a [Proveedor](https://www.chilecompra.cl/glosario/proveedor/) \= “4”   
* En proceso \= “5”   
* Aceptada \= “6”   
* Cancelada \= “9”   
* Recepción Conforme \= “12”   
* Pendiente de Recepcionar \= “13”   
* Recepcionada Parcialmente \= “14”   
* Recepcion Conforme Incompleta \= “15” 

## Tipos de consulta

## Por {código} de orden de compra

**Ejemplo de {codigo} \= 2097-241-SE14**

*https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?codigo=**2097-241-SE14**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844* 

## Por todos los estados del día actual

https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?estado=todos\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844 

## Por todos los estados de una {fecha} específica

**Ejemplo de {fecha} \= 02022014**

https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=02022014\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

## Por {estado} del día actual

**Ejemplo de {estado} \= ACEPTADA** 

{estados} de las órdenes de compra y su nomenclatura: 

Enviada a [Proveedor](https://www.chilecompra.cl/glosario/proveedor/) \= “**enviadaproveedor**“  
Aceptada \= “**aceptada**“  
Cancelada \= “**cancelada**“  
Recepción Conforme \= “**recepcionconforme**“  
Pendiente de Recepcionar \= “**pendienterecepcion**“  
Recepcionada Parcialmente \= “**recepcionaceptadacialmente**“  
Recepcion Conforme Incompleta \= “**recepecionconformeincompleta**“  
todos \= “**todos**“ *(muestra todos los estados posibles antes señalados)* 

*https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=02022014\&estado=**{estado}**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*

*https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=02022014\&estado=**aceptada**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*

## Por {código} de organismo público

**Ejemplo de {CódigoOrganismo} \= 694**

https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha={fecha}\&CodigoOrganismo={CódigoOrganismo}\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=02022014\&CodigoOrganismo=6945\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

## Por {código} de proveedor

**Ejemplo de {CódigoProveedor} \= 17793**

https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=02022014\&CodigoProveedor={CódigoProveedor}\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json?fecha=02022014\&CodigoProveedor=17793\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844

## Por {código} de proveedor

Los resultados de las búsquedas son realizadas en base a los números de órdenes de compra enviadas en el día. Los resultados entregados contienen información básica de las órdenes de compra. 

En el caso de la búsqueda por código no importa la fecha, dado que siempre se obtendrá la orden de compra solicitada. El resultado entregado posee información detallada de la orden de compra. 

El formato de la fecha es ddmmaaaa, ejemplo: 12062026, obtendrá las órdenes de compra del día 12 del mes de junio del año 2026\. 

[https://api.mercadopublico.cl/modules/OrdenCompra.aspx](https://api.mercadopublico.cl/modules/OrdenCompra.aspx) 

## Documentación de orden de compra

Cantidad

FechaCreacion 

Version

Listado

Cantidad de órdenes de compra encontradas 

Fecha de consulta

Código de la orden de compra de Mercado Publico

Listado de órdenes de Compra

## ANEXOS

## Tipo orden de compra

## Codigo

## Abreviación

## Descripción

1

OC

Automática

2

D1

[Trato directo](https://www.chilecompra.cl/glosario/trato-directo/) que genera Orden de Compra por [proveedor](https://www.chilecompra.cl/glosario/proveedor/) único.

3

C1

[Trato directo](https://www.chilecompra.cl/glosario/trato-directo/) que genera Orden de Compra por emergencia, urgencia e imprevisto.

4

F3

[Trato directo](https://www.chilecompra.cl/glosario/trato-directo/) que genera Orden de Compra por confidencialidad.

5

G1

[Trato directo](https://www.chilecompra.cl/glosario/trato-directo/) que genera Orden de Compra por naturaleza de negociación.

6

R1

Orden de compra menor a 3UTM

7

CA

Orden de compra sin resolución.

8

SE

Sin emisión automática

9

[CM](https://www.chilecompra.cl/glosario/cm/)

[Convenio Marco](https://www.chilecompra.cl/glosario/convenio-marco/)

10

FG

[Trato Directo](https://www.chilecompra.cl/glosario/trato-directo/) (Art. 8 letras f y g - Ley 19.886)

11

TL

[Convenio Marco](https://www.chilecompra.cl/glosario/convenio-marco/) – Tienda de Libros (Obsoleto)

12

MC

Microcompra

13

[AG](https://www.chilecompra.cl/glosario/ag/)

Compra Ágil

14

CC

Compra Coordinada

## Unidad Monetaria

## Valor

## Descripción

CLP

CLF

USD

UTM

EUR

Peso Chileno

Unidad de Fomento

Dólar Americano

Euro

Unidad Tributaria Mensual

## Tipo de despacho

## Valor

## Descripción

7

9

12

14

20

21

22

Despachar a Dirección de envío

Despachar según programa adjuntado

Otra Forma de Despacho, Ver Instruc

Retiramos de su bodega

Despacho por courier o encomienda aérea

Despacho por courier o encomienda terrestre

A convenir

## Tipo de Pago

## Valor

## Descripción

2

1

39

46

47

48

49

30 días contra la recepción de la factura

15 días contra la recepción de la factura

Otra forma de pago

50 días contra la recepción de la factura

60 días contra la recepción de la factura

A 45 días

A más de 30 días

**4 Codigos de organismos publicos y proveedores**  
Para obtener el código de un [**proveedor**](https://www.chilecompra.cl/glosario/proveedor/) debes consumir el siguiente código indicando el RUT de la empresa a buscar (debe incluir puntos, guión y dígito verificador): 

*https://api.mercadopublico.cl/servicios/v1/Publico/Empresas/BuscarProveedor?rutempresaproveedor=**70.017.820-k**\&ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*   
   
Dónde: 

* Código Empresa: Código de la empresa [Proveedor](https://www.chilecompra.cl/glosario/proveedor/). Ejemplo de **{CódigoEmpresa}** = 17793   
* Nombre Empresa: Nombre de la empresa [Proveedor](https://www.chilecompra.cl/glosario/proveedor/). Ejemplo de **{NombreEmpresa}** = “Cámara de Comercio de Santiago A.G. (CCS)”. 

Para obtener el código de un **organismo público** debes escribir el siguiente texto, el cual entrega como resultado una lista de todos los organismos públicos de la plataforma Mercado Público: 

*https://api.mercadopublico.cl/servicios/v1/Publico/Empresas/BuscarComprador?ticket=F8537A18-6766-4DEF-9E59-426B4FEE2844*

Dónde: 

* Código Empresa: Código del organismo público. Ejemplo de **{CódigoEmpresa}** = 6945   
* Nombre Empresa: Nombre del organismo público. Ejemplo de **{NombreEmpresa}** = “Dirección de Compras y Contratación Pública”. 

