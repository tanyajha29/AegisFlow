--
-- PostgreSQL database dump
--

\restrict MNSuicAiR693tZLimsQkjafwViiRhCqvwk3z3YfpnADddWk62LoqfkwfXMW23N1

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg12+1)
-- Dumped by pg_dump version 15.17 (Debian 15.17-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- Name: scans; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.scans (
    id integer NOT NULL,
    user_id integer NOT NULL,
    file_name character varying(255) NOT NULL,
    scan_date timestamp without time zone NOT NULL,
    risk_score double precision NOT NULL,
    security_score double precision NOT NULL,
    total_findings integer NOT NULL,
    critical_count integer NOT NULL,
    high_count integer NOT NULL,
    medium_count integer NOT NULL,
    low_count integer NOT NULL,
    total_issues integer NOT NULL,
    vulnerability_snapshot json NOT NULL
);


ALTER TABLE public.scans OWNER TO admin;

--
-- Name: scans_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.scans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scans_id_seq OWNER TO admin;

--
-- Name: scans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.scans_id_seq OWNED BY public.scans.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    mfa_enabled boolean NOT NULL,
    mfa_secret_encrypted text,
    backup_codes text
);


ALTER TABLE public.users OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vulnerabilities; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.vulnerabilities (
    id integer NOT NULL,
    scan_id integer NOT NULL,
    name character varying(255) NOT NULL,
    severity character varying(50) NOT NULL,
    file_name character varying(255) NOT NULL,
    line_number integer,
    description text NOT NULL,
    remediation text NOT NULL,
    cwe_reference character varying(50),
    code_snippet text
);


ALTER TABLE public.vulnerabilities OWNER TO admin;

--
-- Name: vulnerabilities_id_seq; Type: SEQUENCE; Schema: public; Owner: admin
--

CREATE SEQUENCE public.vulnerabilities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vulnerabilities_id_seq OWNER TO admin;

--
-- Name: vulnerabilities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: admin
--

ALTER SEQUENCE public.vulnerabilities_id_seq OWNED BY public.vulnerabilities.id;


--
-- Name: scans id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scans ALTER COLUMN id SET DEFAULT nextval('public.scans_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vulnerabilities id; Type: DEFAULT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.vulnerabilities ALTER COLUMN id SET DEFAULT nextval('public.vulnerabilities_id_seq'::regclass);


--
-- Data for Name: scans; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.scans (id, user_id, file_name, scan_date, risk_score, security_score, total_findings, critical_count, high_count, medium_count, low_count, total_issues, vulnerability_snapshot) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.users (id, email, password_hash, created_at, mfa_enabled, mfa_secret_encrypted, backup_codes) FROM stdin;
\.


--
-- Data for Name: vulnerabilities; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.vulnerabilities (id, scan_id, name, severity, file_name, line_number, description, remediation, cwe_reference, code_snippet) FROM stdin;
\.


--
-- Name: scans_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.scans_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.users_id_seq', 1, false);


--
-- Name: vulnerabilities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.vulnerabilities_id_seq', 1, false);


--
-- Name: scans scans_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scans
    ADD CONSTRAINT scans_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vulnerabilities vulnerabilities_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.vulnerabilities
    ADD CONSTRAINT vulnerabilities_pkey PRIMARY KEY (id);


--
-- Name: ix_scans_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_scans_id ON public.scans USING btree (id);


--
-- Name: ix_scans_user_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_scans_user_id ON public.scans USING btree (user_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: admin
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_vulnerabilities_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_vulnerabilities_id ON public.vulnerabilities USING btree (id);


--
-- Name: ix_vulnerabilities_scan_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX ix_vulnerabilities_scan_id ON public.vulnerabilities USING btree (scan_id);


--
-- Name: scans scans_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scans
    ADD CONSTRAINT scans_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: vulnerabilities vulnerabilities_scan_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.vulnerabilities
    ADD CONSTRAINT vulnerabilities_scan_id_fkey FOREIGN KEY (scan_id) REFERENCES public.scans(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict MNSuicAiR693tZLimsQkjafwViiRhCqvwk3z3YfpnADddWk62LoqfkwfXMW23N1

