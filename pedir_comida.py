import sqlite3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

class PedidoApp(App):
    def build(self):
        self.conectar_bd()

        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.label = Label(text="Escolha seu pedido", font_size=20)
        self.layout.add_widget(self.label)

        self.btn_pizza = Button(text="Pedir Pizza", font_size=18)
        self.btn_pizza.bind(on_press=lambda x: self.confirmar_pedido("Pizza"))
        self.layout.add_widget(self.btn_pizza)

        self.btn_hamburguer = Button(text="Pedir Hambúrguer", font_size=18)
        self.btn_hamburguer.bind(on_press=lambda x: self.confirmar_pedido("Hambúrguer"))
        self.layout.add_widget(self.btn_hamburguer)

        # Botões de ação (escondidos inicialmente)
        self.btn_confirmar = Button(text="Confirmar", font_size=18, on_press=self.fazer_pedido)
        self.btn_voltar = Button(text="Voltar", font_size=18, on_press=self.voltar)
        self.btn_cancelar = Button(text="Cancelar", font_size=18, on_press=self.cancelar)

        # Botões para aumentar/diminuir a quantidade
        self.btn_menos = Button(text="-", font_size=18, on_press=self.diminuir_quantidade)
        self.btn_mais = Button(text="+", font_size=18, on_press=self.aumentar_quantidade)
        self.label_quantidade = Label(text="Quantidade: 1", font_size=18)

        self.quantidade = 1  # Quantidade inicial

        return self.layout

    def conectar_bd(self):
        """ Cria o banco de dados e a tabela se não existirem """
        self.conn = sqlite3.connect("pedidos.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                quantidade INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def confirmar_pedido(self, item):
        """ Mostra mensagem de confirmação e exibe botões de ação """
        self.item_selecionado = item
        self.quantidade = 1  # Sempre inicia com 1 unidade
        self.label.text = f"Você escolheu {item}, certo?"

        # Esconder botões de pedido e mostrar opções de confirmação
        self.layout.clear_widgets()
        self.layout.add_widget(self.label)

        # Adicionando botões de quantidade
        box_qtd = BoxLayout(orientation='horizontal', spacing=10)
        box_qtd.add_widget(self.btn_menos)
        box_qtd.add_widget(self.label_quantidade)
        box_qtd.add_widget(self.btn_mais)

        self.layout.add_widget(box_qtd)

        # Adicionando botões de ação
        self.layout.add_widget(self.btn_confirmar)
        self.layout.add_widget(self.btn_voltar)
        self.layout.add_widget(self.btn_cancelar)

    def aumentar_quantidade(self, instance):
        """ Aumenta a quantidade do pedido """
        self.quantidade += 1
        self.label_quantidade.text = f"Quantidade: {self.quantidade}"

    def diminuir_quantidade(self, instance):
        """ Diminui a quantidade do pedido (mínimo 1) """
        if self.quantidade > 1:
            self.quantidade -= 1
            self.label_quantidade.text = f"Quantidade: {self.quantidade}"

    def fazer_pedido(self, instance):
        """ Confirma o pedido e armazena no banco de dados """
        self.cursor.execute("INSERT INTO pedidos (item, quantidade) VALUES (?, ?)", 
                            (self.item_selecionado, self.quantidade))
        self.conn.commit()

        self.label.text = f"Pedido enviado: {self.quantidade}x {self.item_selecionado}"
        Clock.schedule_once(self.mensagem_escolha, 2)  # Após 2 segundos, exibe "Ótima escolha."

    def mensagem_escolha(self, dt):
        """ Exibe a mensagem 'Ótima escolha.' """
        self.label.text = "Ótima escolha."
        Clock.schedule_once(self.mensagem_final, 2)  # Após 2 segundos, exibe "Obrigado e volte sempre!"

    def mensagem_final(self, dt):
        """ Exibe a mensagem final e depois mostra os pedidos salvos """
        self.label.text = "Obrigado e volte sempre!"
        Clock.schedule_once(self.mostrar_pedidos, 2)  # Aguarda antes de mostrar os pedidos

    def mostrar_pedidos(self, dt):
        """ Busca e exibe os pedidos armazenados no banco """
        self.cursor.execute("SELECT quantidade, item FROM pedidos")
        pedidos = self.cursor.fetchall()

        pedidos_texto = "\n".join([f"{qtd}x {item}" for qtd, item in pedidos]) if pedidos else "Nenhum pedido realizado."
        self.label.text = f"Histórico de pedidos:\n{pedidos_texto}"
        Clock.schedule_once(self.resetar_tela, 3)  # Aguarda antes de resetar a tela

    def voltar(self, instance):
        """ Retorna à tela inicial sem confirmar o pedido """
        self.label.text = "Escolha seu pedido"
        self.resetar_tela()

    def cancelar(self, instance):
        """ Cancela o pedido e retorna à tela inicial """
        self.label.text = "Pedido cancelado!"
        Clock.schedule_once(self.resetar_tela, 2)  # Aguarda um pouco antes de voltar à tela inicial

    def resetar_tela(self, dt=0):
        """ Retorna à tela inicial com os botões de pedido visíveis """
        self.layout.clear_widgets()
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.btn_pizza)
        self.layout.add_widget(self.btn_hamburguer)

if __name__ == '__main__':
    PedidoApp().run()