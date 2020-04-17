--
-- PostgreSQL database dump
--

-- Dumped from database version 11.7 (Debian 11.7-0+deb10u1)
-- Dumped by pg_dump version 11.7 (Debian 11.7-0+deb10u1)

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

SET default_with_oids = false;

--
-- Name: wordcloud_tutors; Type: TABLE; Schema: public; Owner: wordclouduser
--

CREATE TABLE public.wordcloud_tutors (
    tutor_id integer NOT NULL,
    tutor_source_id character varying(50) NOT NULL,
    tutor_course character varying(255) NOT NULL,
    tutor_course_run integer NOT NULL,
    tutor_first_name character varying(255) NOT NULL,
    tutor_last_name character varying(255) NOT NULL,
    tutor_team_role character varying(255),
    tutor_user_role character varying(255)
);


ALTER TABLE public.wordcloud_tutors OWNER TO wordclouduser;

--
-- Name: wordcloud_tutors_tutor_id_seq; Type: SEQUENCE; Schema: public; Owner: wordclouduser
--

CREATE SEQUENCE public.wordcloud_tutors_tutor_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wordcloud_tutors_tutor_id_seq OWNER TO wordclouduser;

--
-- Name: wordcloud_tutors_tutor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wordclouduser
--

ALTER SEQUENCE public.wordcloud_tutors_tutor_id_seq OWNED BY public.wordcloud_tutors.tutor_id;


--
-- Name: wordcloud_tutors tutor_id; Type: DEFAULT; Schema: public; Owner: wordclouduser
--

ALTER TABLE ONLY public.wordcloud_tutors ALTER COLUMN tutor_id SET DEFAULT nextval('public.wordcloud_tutors_tutor_id_seq'::regclass);


--
-- Name: wordcloud_tutors wordcloud_tutors_pkey; Type: CONSTRAINT; Schema: public; Owner: wordclouduser
--

ALTER TABLE ONLY public.wordcloud_tutors
    ADD CONSTRAINT wordcloud_tutors_pkey PRIMARY KEY (tutor_id);


--
-- PostgreSQL database dump complete
--
