from sql_alchemy import banco

class SiteModel(banco.Model):

    __tablename__ = 'sites' # nome da tabela no banco de dados

    site_id = banco.Column(banco.String, primary_key=True)
    url = banco.Column(banco.String(40))
    hoteis = banco.relationship('HotelModel', backref='site', lazy='dynamic') # lista de objetos Hoteis.

    def __init__(self, url):
        self.url = url

    def json(self):
        return {
            'site_id': self.site_id,
            'url': self.url,
            'hoteis': [hotel.json() for hotel in self.hoteis]
        }

    @classmethod
    def find_site(cls, url):
        site = cls.query.filter_by(url=url).first()
        if site:
            return site
        return None

    def save_site(self):
        banco.session.add(self)
        banco.session.commit()

    def delete_site(self):
        banco.session.delete(self)
        banco.session.commit()
