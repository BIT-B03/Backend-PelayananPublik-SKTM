from extension import ma
from marshmallow import fields, validate, post_load

class KartuKeluargaCreateSchema(ma.Schema):
    no_kk = fields.String(required=True, validate=[validate.Length(equal=16), validate.Regexp(r"^\d{16}$")])
    nama_kepala_keluarga = fields.String(required=True)
    alamat = fields.String(allow_none=True)
    foto_kk = fields.String(allow_none=True)
    tingkat_pendidikan_kepala_keluarga = fields.String(allow_none=True)
    anak_tidak_sekolah = fields.String(allow_none=True)

    @post_load
    def make_kk(self, data, **kwargs):
        if 'no_kk' in data and isinstance(data['no_kk'], str):
            data['no_kk'] = int(data['no_kk'])
        data.setdefault('status', 'P')

        from models.kartukeluargaModel import KartuKeluarga
        from models.humancapitalModel import HumanCapital

        kk = KartuKeluarga(
            no_kk=data.get('no_kk'),
            nama_kepala_keluarga=data.get('nama_kepala_keluarga'),
            alamat=data.get('alamat'),
            foto_kk=data.get('foto_kk'),
            status=data.get('status'),
            nik=data.get('nik')
        )

        tingkat = data.get('tingkat_pendidikan_kepala_keluarga')
        anak_tdk = data.get('anak_tidak_sekolah')
        if tingkat is not None or anak_tdk is not None:
            hc = HumanCapital(
                nik=kk.nik,
                tingkat_pendidikan_kepala_keluarga=tingkat,
                anak_tidak_sekolah=anak_tdk,
                status='P'
            )
            kk._human_capital = hc

        return kk

class KartuKeluargaSchema(ma.Schema):
    id_kk = fields.Integer()
    no_kk = fields.Integer()
    nama_kepala_keluarga = fields.String()
    alamat = fields.String(allow_none=True)
    foto_kk = fields.String(allow_none=True)
    status = fields.String()
    nik = fields.Integer()

class HumanCapitalSchema(ma.Schema):
    id_human_capital = fields.Integer()
    nik = fields.Integer()
    tingkat_pendidikan_kepala_keluarga = fields.String(allow_none=True)
    anak_tidak_sekolah = fields.String(allow_none=True)
    status = fields.String()

kk_schema = KartuKeluargaSchema()
kks_schema = KartuKeluargaSchema(many=True)
kk_create_schema = KartuKeluargaCreateSchema()
hc_schema = HumanCapitalSchema()