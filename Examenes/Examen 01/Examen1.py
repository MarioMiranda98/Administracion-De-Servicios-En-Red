import paramiko, getpass, time
from graphviz import Digraph

dispositivos = ["148.204.56.1"]
comandos = [
	"username pirata privilege 15 password pirata\n",
	"end\n", "write\n"
]
	
shIpRoute = "show ip route\n"
username = "admin"
password = "firulais"

maxBuffer = 65535

direcciones = {}
via = {}
listaVia = []
routersRepetidos = []
listaDirecciones = []

def limpiarBuffer(conexion):
	global maxBuffer
	if conexion.recv_ready():
		return conexion.recv(maxBuffer) 

def crearUsuario(router, nueva, dispositivo):
	global routersRepetidos
	global maxBuffer
	global direcciones
	
	print("Este es el router: "+router)
	routersRepetidos.append(router)
	salida = limpiarBuffer(nueva)
	
	for comando in comandos:
		nueva.send(comando)
		time.sleep(2)
		salida = nueva.recv(maxBuffer)
		print(salida)
		
	salida = limpiarBuffer(nueva)
	nueva.send(shIpRoute)
	time.sleep(2)
	salida = nueva.recv(maxBuffer)
	
	resultado = salida.decode("utf-8")
	filas = resultado.splitlines()
	
	for linea in filas:
		if "via" in linea:
			aux = linea.split("via ")
			aux = aux[1].split(',')
			if aux[0] not in dispositivos:
				dispositivos.append(aux[0])
			if aux[0] not in listaVia:
				listaVia.append(aux[0])
			via[dispositivo] = listaVia
            
		if "directly" in linea:
			ip = linea.split(" ")
			if ip[7] in direcciones.keys():
				if router not in direcciones[ip[7]]:
					listaAuxiliar = direcciones[ip[7]]
					listaAuxiliar.append(router)
				direcciones[ip[7]] = listaAuxiliar
			else:
				direcciones[ip[7]] = [router]
	nueva.close()
                
		
def analizar(dispositivo):
	global listaDirecciones
	global username
	global password
	global routersRepetidos
	
	print(dispositivo)
	conexion = paramiko.SSHClient()
	conexion.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	try:
		resultado = conexion.connect(dispositivo, username = username, password = password, look_for_keys = False, allow_agent = False)
	except:
		print("Conexion no exitosa")
		return 
				
	nueva = conexion.invoke_shell()
	salida = limpiarBuffer(nueva)
	nueva.send("terminal length 0\n")
	time.sleep(3)
	salida = limpiarBuffer(nueva)
	nueva.send("conf t\n")
	time.sleep(3)
	
	routerActual = salida.decode("utf-8")
	aux = routerActual.split("#")
	cadenaRouter = aux[0]
	longitud = len(cadenaRouter)
	router = cadenaRouter[(longitud - 2) : longitud]
	
	if (router in routersRepetidos):
		print("Router ya analizado")
	else: 
		crearUsuario(router, nueva, dispositivo)
	
def obtenerEstilos(miGrafica):
	global direcciones
	
	aux = []
	for id in direcciones.keys():
		aux = id.split(".")
		dif = int(aux[0])
		dif2 = int(aux[2])
		
		for r in direcciones[id]:
			if dif > 9:
				if dif2 != 56:
					miGrafica.node("PC" + r, shape = "box", color = "mediumblue", style = "filled", fillcolor = "lightblue")
				else: 
					miGrafica.node("PCV", shape = "box", color = "mediumblue", style = "filled", fillcolor = "lightblue")
					miGrafica.node("Sw", shape = 'box3d', color = "green3", orientation = '180', style = 'filled', fillcolor = "darkolivegreen3")
					miGrafica.edge("PCV",'Sw')
			else:
				 miGrafica.node(r, shape = "cylinder", style = "filled", fillcolor = "antiquewhite3")
				 
	return miGrafica
	
def hacerConexiones(miGrafica):
	global direcciones
	
	aux = []
	aux2 = []
	for id in direcciones.keys():
		aux = id.split(".")
		dif = int(aux[0])
		dif2 = int(aux[2])
		
		if dif > 9:
			if dif2 == 56:
				aux2 = direcciones[id]
				indice = 0
				for x in aux2:
					miGrafica.edge("Sw", aux2[indice])
					print("PCV con " + aux2[indice])
					indice += 1
			else:
				aux2 = direcciones[id]
				indice = 0
				for x in aux2:
					miGrafica.edge("PC" + x, aux2[indice])
					print("PC" + x + " con " + aux2[indice])
					indice += 1
		else:
			aux2 = direcciones[id]
			if len(aux2) == 2:
				miGrafica.edge(aux2[0], aux2[1])
			else:
				continue

	return miGrafica
			
def graficar():
	miGrafica = Digraph(comment = "Mi_red")
	miGrafica.edge_attr.update(arrowhead = 'none')
	
	miGrafica = obtenerEstilos(miGrafica)
	miGrafica = hacerConexiones(miGrafica)
	
	miGrafica.render("Final", format = "png")
    miGrafica.render("Final", format = "dot")
	
def main():
	global direcciones
	
	for dispositivo in dispositivos:
		analizar(dispositivo)
		
	for item in direcciones.items():
		print(item)
    	
	graficar()
    
main()
