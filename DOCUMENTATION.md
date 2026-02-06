# Jupyterlab-Guriang Project Documentation

Project ini adalah implementasi dari jupyterhub dan jupyterlab pada server guriang yang di-manage menggunakan docker swarm.

## Struktur Project

Project ini secara garis besar menjalankan 3 service:
- Jupyterhub: Sebagai master dan juga login node untuk user.
- Jupyterlab: Sebagai workspace user.
- Registry: Sebagai hub untuk passing container jupyterlab yang sudah di-build.

## Spawner (Docker Swarm)
Jupyterhub berjalan di ```magrathea```, sedangkan Jupyterlab akan berjalan dan  spawn di ```whale01``` (ataupun server lain). Untuk menambahkan worker pada server lain, jalankan command berikut di ```magrathea```:
```bash
docker swarm join-token worker
```
kemudian akan tampil ```docker swarm join --token {{token}} 172.16.1.12:2377``` yang bisa dicopy untuk mendaftarkan node lain menjadi worker dari swarm-network yang sudah di-init di ```magrathea```.

Untuk melakukan placement jupyterlab di luar magrathea (worker), hapus ```#``` pada file ```jupyterhub_config.py``` pada bagian ini:

```bash
#c.SwarmSpawner.extra_placement_spec = {
#    'constraints': ['node.role == worker']
#}
```

## Instalasi Container
Dikarenakan keterbatasan jaringan kampus yang tidak bisa access (permission denied) ke package repository ```Ubuntu```, lakukan build container diluar jaringan kampus. Project folder bisa diambil dari github repositori [ini](https://github.com/umaraziz10/jupyterlab-guriang). Atau lakukan cloning menggunakan command:

```bash
git clone https://github.com/umaraziz10/jupyterlab-guriang
```

lalu build dockernya menjadi image:
```bash
mv jupyterlab-guriang/ jupyterlab/
cd jupyterlab/
docker build -t {image_name}:{tag} .
```

## Maintain Container
Setelah docker berhasil di-build (baik secara lokal diluar jaringan kampus atau di server), lakukan tagging dengan menggunakan command:
```bash
docker tag {nama_image}:{tag} 172.16.1.12:5000/{nama_image}:{tag}
```

kemudian push container ke registry yang berjalan di port 5000:
```bash
docker push 172.16.1.12:5000/{nama_image}:{tag}
```

Jika berhasil, lakukan pull pada node ```worker``` dengan menjalankan command:
```bash
docker pull 172.16.1.12:5000/{nama_image}:{tag}
```

Jika ingin mengganti image jupyterlab dengan versi yang baru saja dibuat, ubah file ```docker-compose.yml``` pada line 32 dan 44 menjadi:
```bash
(32)DOCKER_JUPYTER_IMAGE: "172.16.1.12:5000/{nama_image}:{tag}"

(44)image: "172.16.1.12:5000/{nama_image}:{tag}"
```

## Running Project
Untuk menjalankan project, pergi ke ```/opt/umar-jupy-swarm-try```, atau buat folder khusus untuk production (sangat disarankan) dari folder yang sudah dirapihkan:
```bash
cp /home/umar/jupyter-prod /opt/{nama_folder}
cd /opt/{nama_folder}
```
lalu jalankan compose yang sudah dibuat dengan command:
```bash
docker compose up -d
```
maka akan ada 2 service yang langsung berjalan, yakni jupyterhub di port ```88``` dan juga docker registry di port ```5000```.

Jika mengunjungi ```https://{alamat_website}:88/``` dan melakukan login, maka container akan otomatis spawn pada server worker(jika sudah disetup). Untuk mengecek container user yang sedang berjalan, gunakan command:
```bash
docker service ls
```
