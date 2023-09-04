'''
Grupo : Christian Dambock Gomes , Guilherme Lozano Borges, Wellington Lira
'''
'''
O objetivo é fazer um scraper que navega no site e coleta as informações, trata e gerar o resultado em formato json

O que devemos buscar de cada Pokémon obrigatoriamente:

- Número v
- URL da páginav
- Nome v
- Próximas evoluções do Pokémon se houver (PokéNum, nome e URL)
- Tamanho v
- Peso v
- Tipos (água, veneno, ...) v
- Habilidades (link para outra página)
    - URL da página v
    - Nome v
    - Descrição do efeitov

- Tratamento de dados
    - Remover dados nulos ou inválidos
    - Transformação de dados
'''

'''
Professor , para passar o tempo aproveitamos para adicionar , as habilidades, tanto normais quanto hiden, especie e também aonde se pode encontar o pokemon
'''
import scrapy
class PokeSpider(scrapy.Spider):
    name = 'pokespider'
    start_urls = ['https://pokemondb.net/pokedex/all']

    def parse(self, response):
        linhas = response.css('table#pokedex > tbody > tr')
        # for linha in linhas:
        linha = linhas[251]
        link = linha.css("td:nth-child(2) > a::attr(href)")
        yield response.follow(link.get(), self.parse_pokemon)

    def parse_pokemon(self, response):
        link = response.url
        nome = response.css('main#main > h1::text')
        id = response.css("table.vitals-table > tbody > tr:nth-child(1) > td> strong::text")
        type1 = response.selector.xpath("string(//table[@class='vitals-table'][1]/tbody/tr[2]/td)")
        height = response.css("table.vitals-table > tbody > tr:nth-child(4) > td::text")
        weight = response.css("table.vitals-table > tbody > tr:nth-child(5) > td::text")
        ability_Link = response.css("table.vitals-table > tbody > tr:nth-child(6) > td> span > a::attr(href)")

        evolution = response.xpath("//span[@class='infocard-lg-data text-muted']")
        evolutions = []
        evolution_names_repeated= set() 

        for e in evolution:
          evolution_name = e.xpath(".//a[1]//text()").get()
          if nome.get() != evolution_name and evolution_name not in evolution_names_repeated:
              evolutions.append({
                  "Name": evolution_name,                
                  "Link": "https://pokemondb.net" + e.xpath(".//a[1]//@href").get(),
                  "Number": e.xpath(".//small[1]//text()").get(),
              })
              evolution_names_repeated.add(evolution_name)
        yield response.follow(ability_Link.get(), self.parse_pokemon_ability, meta={
            'pokemon_data': {
              "Pokemon Data":{
                "Name": nome.get(),
                "Link": link,
                "Id": id.get(),
                "Type": ["|" + type1.get().replace("\n" ,"").replace(" " ,"|")],
                "Height": height.get(),
                "Weight": weight.get(),
              },
                "Evolutions": evolutions
            }
        })
    def parse_pokemon_ability(self, response):
        link = response.url
        ability = response.css("main#main > h1::text")
        description1 = response.selector.xpath("string(//div[@class='grid-col span-md-12 span-lg-6']/p)")

        pokemon_data = response.meta['pokemon_data']

        pokemon_data["Ability"] = {
            "Ability": ability.get(),
            "Ability Link": link,
            "Description": description1.getall()
        }

        yield pokemon_data
