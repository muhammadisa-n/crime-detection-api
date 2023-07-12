-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Waktu pembuatan: 12 Jul 2023 pada 01.09
-- Versi server: 10.4.28-MariaDB
-- Versi PHP: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `crime_detection`
--

-- --------------------------------------------------------

--
-- Struktur dari tabel `histories`
--

CREATE TABLE `histories` (
  `id` int(11) NOT NULL,
  `filename` varchar(250) DEFAULT NULL,
  `tanggal` timestamp NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `latitude` varchar(500) DEFAULT NULL,
  `longatitude` varchar(500) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `histories`
--

INSERT INTO `histories` (`id`, `filename`, `tanggal`, `latitude`, `longatitude`) VALUES
(3, 'stealing.mp4', '2023-07-11 20:54:48', NULL, NULL),
(4, 'stealing.mp4', '2023-07-11 22:49:20', NULL, NULL);

-- --------------------------------------------------------

--
-- Struktur dari tabel `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `fullname` varchar(30) NOT NULL,
  `email` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `no_hp` varchar(15) DEFAULT NULL,
  `is_verify` enum('not verify','verified') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `token` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data untuk tabel `users`
--

INSERT INTO `users` (`id`, `fullname`, `email`, `password`, `address`, `no_hp`, `is_verify`, `created_at`, `updated_at`, `token`) VALUES
(1, 'Muhisa', 'muhammadisa226@gmail.com', 'pbkdf2:sha256:600000$ToFrPEysBMTp05B3$ffe96481c054ffefa68a59060efdf8d9d5d2ce113fc619c9d8bc307e27e449cf', 'tegal', '087833380742', 'verified', '2023-06-22 17:55:54', '2023-06-22 18:05:01', NULL),
(2, 'Muhammad Isa Nuruddin', 'muhammadisa0704@gmail.com', 'pbkdf2:sha256:600000$Mspd5zr8pomyEf6G$53b4e76171de99ebdc14a1ae0daf0f0043f8005490ac8d0cf3512ab4355e02ee', NULL, NULL, 'verified', '2023-06-22 17:57:04', '2023-06-22 17:57:48', NULL);

--
-- Indexes for dumped tables
--

--
-- Indeks untuk tabel `histories`
--
ALTER TABLE `histories`
  ADD PRIMARY KEY (`id`);

--
-- Indeks untuk tabel `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT untuk tabel yang dibuang
--

--
-- AUTO_INCREMENT untuk tabel `histories`
--
ALTER TABLE `histories`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT untuk tabel `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
