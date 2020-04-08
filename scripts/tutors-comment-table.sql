--
-- Name: wordcloud_tutors; Type: TABLE; Schema: public; Owner: wordcloud
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

ALTER TABLE public.wordcloud_tutors OWNER TO wordcloud;

--
-- Name: wordcloud_tutors_tutor_id_seq; Type: SEQUENCE; Schema: public; Owner: wordcloud
CREATE SEQUENCE public.wordcloud_tutors_tutor_id_seq
AS integer
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;

ALTER TABLE public.wordcloud_tutors_tutor_id_seq OWNER TO wordcloud;

--
-- Name: wordcloud_tutors_tutor_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: wordcloud
ALTER SEQUENCE public.wordcloud_tutors_tutor_id_seq OWNED BY public.wordcloud_tutors.tutor_id;