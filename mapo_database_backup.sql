--
-- PostgreSQL database dump
--

\restrict t04dK2y1heMaXZFOfmNFgn8J2OyFsMYrz8haCGBRCh17XlYmf2DqMitL1IUl4UA

-- Dumped from database version 17.6 (Debian 17.6-1.pgdg13+1)
-- Dumped by pg_dump version 17.6 (Debian 17.6-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: person; Type: TABLE; Schema: public; Owner: mapo
--

CREATE TABLE public.person (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    last_name character varying NOT NULL,
    document_type character varying NOT NULL,
    document_number character varying NOT NULL
);


ALTER TABLE public.person OWNER TO mapo;

--
-- Name: product; Type: TABLE; Schema: public; Owner: mapo
--

CREATE TABLE public.product (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL,
    description character varying NOT NULL,
    category_id uuid,
    image_url character varying
);


ALTER TABLE public.product OWNER TO mapo;

--
-- Name: role; Type: TABLE; Schema: public; Owner: mapo
--

CREATE TABLE public.role (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying NOT NULL
);


ALTER TABLE public.role OWNER TO mapo;

--
-- Name: user; Type: TABLE; Schema: public; Owner: mapo
--

CREATE TABLE public."user" (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    uid character varying NOT NULL,
    email character varying NOT NULL,
    person_id uuid NOT NULL
);


ALTER TABLE public."user" OWNER TO mapo;

--
-- Name: user_role; Type: TABLE; Schema: public; Owner: mapo
--

CREATE TABLE public.user_role (
    user_id uuid NOT NULL,
    role_id uuid NOT NULL
);


ALTER TABLE public.user_role OWNER TO mapo;

--
-- Data for Name: person; Type: TABLE DATA; Schema: public; Owner: mapo
--

COPY public.person (id, name, last_name, document_type, document_number) FROM stdin;
7f0f8eb0-3b98-4e4f-be4f-043b73750142	test	admin	CC	1111111111
d54a97f9-281d-465c-91e5-a4274e3295bb	test	superadmin	CC	1111111111
8ae626c2-cec4-46f2-81e4-a7bdc8f809a9	test	user	CC	1111111111
86421a57-68c9-4d25-a1d8-0ab096feef84	Test	User	CC	987654321
\.


--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: mapo
--

COPY public.product (id, name, description, category_id, image_url) FROM stdin;
3b9341f6-4f55-4f39-b7a9-051cb1eccdc3	Chunky perro adulto	concentrado	\N	https://solucionesdinamicassdi.com/6818/chun.jpg
e600ae6d-4831-4ab7-96da-875e32cc9277	Monello adulto raza pequeña	concentrado	\N	https://http2.mlstatic.com/D_NQ_NP_622585-MLU54967651527_042023-O.webp
695ef597-3748-408f-92dc-242ad8615574	Chunky cats	concentrado	\N	https://acdn-us.mitiendanube.com/stores/131/324/products/chunky-cats-x-8-kg1-32340a5e618525185415122787661527-640-0.jpg
1de595da-4c2e-4f75-821c-6d3644c35aee	Simparica TRIO 10-20	Antipulgas	\N	https://acdn-us.mitiendanube.com/stores/131/324/products/simparica-trio-24-mg-c144f1d4bf84b7677a17037323961127-1024-1024.jpg
b78ac03c-1190-46e7-9111-7c9b49471b14	asdsadsa	sadsad	\N	\N
13ba5eaf-1fd9-4895-bfff-e44c52df5620	ASDASD	ADSA	\N	\N
\.


--
-- Data for Name: role; Type: TABLE DATA; Schema: public; Owner: mapo
--

COPY public.role (id, name) FROM stdin;
6c26db3a-4bf7-4cb8-a0b3-b3ee4765d324	ADMIN
46f88b8a-f668-41c6-b1ca-23cbfab93127	SUPERADMIN
2610870b-e576-48f9-9a05-505b00e7daf5	USER
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: mapo
--

COPY public."user" (id, uid, email, person_id) FROM stdin;
4ab323f5-1617-48a9-8f0c-a929d9ffe14c	SCdFTRoA7kYZ4ZqjjiJiP7IMNTu2	testuser@x.com	8ae626c2-cec4-46f2-81e4-a7bdc8f809a9
eac3a955-3f84-4bf7-99b5-4f15dd93b388	JprEgWR3Q8PIu6lBn1vT4okkPCD3	testadmin@x.com	7f0f8eb0-3b98-4e4f-be4f-043b73750142
795e5887-983d-421a-aa3e-3ec384fa63e9	2Y6e1HKeRQhhdHGelCS827u86mq1	testsuperadmin@x.com	d54a97f9-281d-465c-91e5-a4274e3295bb
b337508b-0135-495f-9e93-cbd86540df08	xUkNdnJRvGaAIoJBZ5Jm5xAQkf33	testpermissions@example.com	86421a57-68c9-4d25-a1d8-0ab096feef84
\.


--
-- Data for Name: user_role; Type: TABLE DATA; Schema: public; Owner: mapo
--

COPY public.user_role (user_id, role_id) FROM stdin;
4ab323f5-1617-48a9-8f0c-a929d9ffe14c	2610870b-e576-48f9-9a05-505b00e7daf5
eac3a955-3f84-4bf7-99b5-4f15dd93b388	2610870b-e576-48f9-9a05-505b00e7daf5
795e5887-983d-421a-aa3e-3ec384fa63e9	2610870b-e576-48f9-9a05-505b00e7daf5
eac3a955-3f84-4bf7-99b5-4f15dd93b388	6c26db3a-4bf7-4cb8-a0b3-b3ee4765d324
795e5887-983d-421a-aa3e-3ec384fa63e9	6c26db3a-4bf7-4cb8-a0b3-b3ee4765d324
795e5887-983d-421a-aa3e-3ec384fa63e9	46f88b8a-f668-41c6-b1ca-23cbfab93127
b337508b-0135-495f-9e93-cbd86540df08	2610870b-e576-48f9-9a05-505b00e7daf5
\.


--
-- Name: person person_pk; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public.person
    ADD CONSTRAINT person_pk PRIMARY KEY (id);


--
-- Name: product product_pk; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pk PRIMARY KEY (id);


--
-- Name: product product_pk_2; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pk_2 UNIQUE (name);


--
-- Name: role role_pk; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public.role
    ADD CONSTRAINT role_pk PRIMARY KEY (id);


--
-- Name: user user_pk; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pk PRIMARY KEY (id);


--
-- Name: user user_pk_2; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pk_2 UNIQUE (email);


--
-- Name: user_role user_role_pk; Type: CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public.user_role
    ADD CONSTRAINT user_role_pk PRIMARY KEY (role_id, user_id);


--
-- Name: user user_person_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: mapo
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_person_id_fk FOREIGN KEY (person_id) REFERENCES public.person(id);


--
-- PostgreSQL database dump complete
--

\unrestrict t04dK2y1heMaXZFOfmNFgn8J2OyFsMYrz8haCGBRCh17XlYmf2DqMitL1IUl4UA

