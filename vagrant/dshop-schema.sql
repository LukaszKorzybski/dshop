--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: plpgsql; Type: PROCEDURAL LANGUAGE; Schema: -; Owner: -
--

CREATE PROCEDURAL LANGUAGE plpgsql;


SET search_path = public, pg_catalog;

--
-- Name: fts_properties_as_str(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION fts_properties_as_str(p_article_id integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    props text;
    prop RECORD;
BEGIN
    props := '';
    FOR prop IN SELECT * FROM main_articleproperty c WHERE article_id = p_article_id LOOP
        props := props || prop.value || '. ';
    END LOOP;
    return props;
END;
$$;


--
-- Name: fts_variants_as_str(integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION fts_variants_as_str(p_article_id integer) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    names text;
    variant main_articlevariant%ROWTYPE;
BEGIN
    names := '';
    FOR variant IN SELECT * FROM main_articlevariant v WHERE article_id = p_article_id LOOP
        names := names || variant.variant || '. ';
    END LOOP;
    return names;
END;
$$;


SET default_with_oids = false;

--
-- Name: auth_group; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_group (
    id integer NOT NULL,
    name character varying(80) NOT NULL
);


--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_group_id_seq OWNED BY auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_group_permissions (
    id integer NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_group_permissions_id_seq OWNED BY auth_group_permissions.id;


--
-- Name: auth_message; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_message (
    id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL
);


--
-- Name: auth_message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_message_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_message_id_seq OWNED BY auth_message.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_permission (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_permission_id_seq OWNED BY auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_user (
    id integer NOT NULL,
    username character varying(30) NOT NULL,
    first_name character varying(30) NOT NULL,
    last_name character varying(30) NOT NULL,
    email character varying(75) NOT NULL,
    password character varying(128) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    is_superuser boolean NOT NULL,
    last_login timestamp with time zone NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_user_groups (
    id integer NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_user_groups_id_seq OWNED BY auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_user_id_seq OWNED BY auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE auth_user_user_permissions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE auth_user_user_permissions_id_seq OWNED BY auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    content_type_id integer,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_admin_log_id_seq OWNED BY django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE django_content_type (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_content_type_id_seq OWNED BY django_content_type.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


--
-- Name: django_site; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE django_site (
    id integer NOT NULL,
    domain character varying(100) NOT NULL,
    name character varying(50) NOT NULL
);


--
-- Name: django_site_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE django_site_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: django_site_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE django_site_id_seq OWNED BY django_site.id;


--
-- Name: main_article; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_article (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    cat_index character varying(255) NOT NULL,
    unit_id integer NOT NULL,
    stock_id integer,
    vat numeric(6,2) NOT NULL,
    net numeric(18,6) NOT NULL,
    gross numeric(18,6) NOT NULL,
    price_calc character varying(2) NOT NULL,
    stock_lvl numeric(14,4) NOT NULL,
    weight numeric(14,4) NOT NULL,
    r_used boolean NOT NULL,
    r_used_shoparticle boolean NOT NULL,
    r_used_variant boolean NOT NULL,
    purchase_gross numeric(18,6),
    purchase_net numeric(18,6),
    supplier_id integer,
    supplier_stock_lvl numeric(14,4) NOT NULL,
    stock_synced boolean NOT NULL,
    stock_last_sync timestamp with time zone,
    supplier_synced boolean NOT NULL,
    supplier_last_sync timestamp with time zone
);


--
-- Name: main_category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_category (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    parent_id integer,
    r_lid_path character varying(255) NOT NULL,
    lft integer NOT NULL,
    rght integer NOT NULL,
    tree_id integer NOT NULL,
    level integer NOT NULL,
    CONSTRAINT main_category_level_check CHECK ((level >= 0)),
    CONSTRAINT main_category_lft_check CHECK ((lft >= 0)),
    CONSTRAINT main_category_rght_check CHECK ((rght >= 0)),
    CONSTRAINT main_category_tree_id_check CHECK ((tree_id >= 0))
);


--
-- Name: main_producer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_producer (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    toplist boolean NOT NULL,
    public boolean NOT NULL,
    exec_time_id integer
);


--
-- Name: main_promotion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_promotion (
    id integer NOT NULL,
    nature character varying(16) NOT NULL,
    cover_variants boolean NOT NULL,
    net numeric(18,6) NOT NULL,
    gross numeric(18,6) NOT NULL,
    price_calc character varying(2) NOT NULL,
    percent numeric(6,2) NOT NULL,
    created timestamp with time zone NOT NULL,
    article_id integer NOT NULL,
    short_desc text NOT NULL
);


--
-- Name: main_shoparticle; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shoparticle (
    id integer NOT NULL,
    article_id integer NOT NULL,
    exec_time_id integer,
    producer_id integer NOT NULL,
    category_id integer NOT NULL,
    specification_id integer,
    param_id integer,
    name character varying(255) NOT NULL,
    public boolean NOT NULL,
    "new" boolean NOT NULL,
    recommended boolean NOT NULL,
    frontpage boolean NOT NULL,
    created timestamp with time zone NOT NULL,
    short_desc text NOT NULL,
    "desc" text NOT NULL,
    variants boolean NOT NULL,
    variants_type character varying(1) NOT NULL,
    variants_name character varying(255) NOT NULL,
    main_variant_name character varying(255) NOT NULL,
    variants_unit_id integer,
    main_variant_qty numeric(14,4),
    r_opinion_count integer NOT NULL,
    r_avg_rating numeric(3,1) NOT NULL,
    r_category_path character varying(500),
    r_main_photo_id integer
);


--
-- Name: fts_articles; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW fts_articles AS
    SELECT sa.id, sa.name, lower((sa.name)::text) AS sort_name, p.name AS producer, ((sa.short_desc || ' '::text) || sa."desc") AS "desc", fts_variants_as_str(sa.id) AS variants, trunc(date_part('epoch'::text, sa.created)) AS created, sa.frontpage, sa.category_id, sa.producer_id, sa."new", sa.recommended, c.r_lid_path AS categories, CASE WHEN (promo.id IS NULL) THEN false WHEN (promo.id IS NOT NULL) THEN true ELSE NULL::boolean END AS promotion, COALESCE(promo.net, a.net) AS net, COALESCE(promo.gross, a.gross) AS gross FROM ((((main_shoparticle sa JOIN main_article a ON ((sa.article_id = a.id))) JOIN main_producer p ON ((sa.producer_id = p.id))) JOIN main_category c ON ((sa.category_id = c.id))) LEFT JOIN main_promotion promo ON ((promo.article_id = a.id))) WHERE ((sa.public = true) AND (p.public = true));


--
-- Name: main_additionallink; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_additionallink (
    id integer NOT NULL,
    location character varying(255) NOT NULL,
    "order" integer NOT NULL,
    title character varying(255) NOT NULL,
    url character varying(255) NOT NULL
);


--
-- Name: main_additionallink_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_additionallink_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_additionallink_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_additionallink_id_seq OWNED BY main_additionallink.id;


--
-- Name: main_address; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_address (
    id integer NOT NULL,
    type character varying(1) NOT NULL,
    first_name character varying(80) NOT NULL,
    last_name character varying(80) NOT NULL,
    company_name character varying(80) NOT NULL,
    nip character varying(255) NOT NULL,
    town character varying(255) NOT NULL,
    street character varying(255) NOT NULL,
    number character varying(255) NOT NULL,
    code character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    second_phone character varying(255) NOT NULL,
    client_id integer NOT NULL,
    base boolean NOT NULL
);


--
-- Name: main_address_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_address_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_address_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_address_id_seq OWNED BY main_address.id;


--
-- Name: main_article_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_article_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_article_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_article_id_seq OWNED BY main_article.id;


--
-- Name: main_articleattachment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_articleattachment (
    id integer NOT NULL,
    article_id integer NOT NULL,
    type_id integer NOT NULL,
    name character varying(255) NOT NULL,
    file character varying(100) NOT NULL,
    listed boolean NOT NULL
);


--
-- Name: main_articleattachment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_articleattachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_articleattachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_articleattachment_id_seq OWNED BY main_articleattachment.id;


--
-- Name: main_articleparam; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_articleparam (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    name_plural character varying(255) NOT NULL,
    explanation text NOT NULL
);


--
-- Name: main_articleparam_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_articleparam_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_articleparam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_articleparam_id_seq OWNED BY main_articleparam.id;


--
-- Name: main_articlephoto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_articlephoto (
    id integer NOT NULL,
    article_id integer NOT NULL,
    main boolean NOT NULL,
    large boolean NOT NULL,
    alt character varying(255) NOT NULL,
    photo character varying(100) NOT NULL
);


--
-- Name: main_articlephoto_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_articlephoto_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_articlephoto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_articlephoto_id_seq OWNED BY main_articlephoto.id;


--
-- Name: main_articleproperty; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_articleproperty (
    id integer NOT NULL,
    article_id integer NOT NULL,
    property_id integer NOT NULL,
    value character varying(1000) NOT NULL
);


--
-- Name: main_articleproperty_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_articleproperty_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_articleproperty_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_articleproperty_id_seq OWNED BY main_articleproperty.id;


--
-- Name: main_articlevariant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_articlevariant (
    id integer NOT NULL,
    article_id integer NOT NULL,
    exec_time_id integer,
    owner_id integer NOT NULL,
    main boolean NOT NULL,
    variant character varying(255) NOT NULL,
    qty numeric(14,4)
);


--
-- Name: main_articlevariant_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_articlevariant_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_articlevariant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_articlevariant_id_seq OWNED BY main_articlevariant.id;


--
-- Name: main_articlevideo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_articlevideo (
    id integer NOT NULL
);


--
-- Name: main_articlevideo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_articlevideo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_articlevideo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_articlevideo_id_seq OWNED BY main_articlevideo.id;


--
-- Name: main_cart; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_cart (
    id integer NOT NULL,
    client_id integer,
    is_order boolean,
    session_key character varying(40)
);


--
-- Name: main_cart_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_cart_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_cart_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_cart_id_seq OWNED BY main_cart.id;


--
-- Name: main_cartitem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_cartitem (
    id integer NOT NULL,
    article_id integer NOT NULL,
    qty numeric(10,4) NOT NULL,
    param_value text NOT NULL,
    created timestamp with time zone NOT NULL,
    cat_index character varying(255) NOT NULL,
    stock_id integer,
    name character varying(255) NOT NULL,
    variant boolean NOT NULL,
    variants_name character varying(255) NOT NULL,
    variant_name character varying(255) NOT NULL,
    unit_short character varying(255) NOT NULL,
    unit_precision numeric(8,4) NOT NULL,
    param boolean NOT NULL,
    param_name character varying(255) NOT NULL,
    param_name_plural character varying(255) NOT NULL,
    weight numeric(14,4) NOT NULL,
    orig_net numeric(18,6) NOT NULL,
    orig_gross numeric(18,6) NOT NULL,
    discount_net numeric(18,6) NOT NULL,
    discount_gross numeric(18,6) NOT NULL,
    owner_id integer NOT NULL,
    discount_price_calc character varying(2)
);


--
-- Name: main_cartitem_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_cartitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_cartitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_cartitem_id_seq OWNED BY main_cartitem.id;


--
-- Name: main_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_category_id_seq OWNED BY main_category.id;


--
-- Name: main_client; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_client (
    id integer NOT NULL,
    type character varying(1) NOT NULL,
    first_name character varying(80) NOT NULL,
    last_name character varying(80) NOT NULL,
    company_name character varying(80) NOT NULL,
    nip character varying(255) NOT NULL,
    town character varying(255) NOT NULL,
    street character varying(255) NOT NULL,
    number character varying(255) NOT NULL,
    code character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    second_phone character varying(255) NOT NULL,
    client_num integer NOT NULL,
    stock_id integer,
    login character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    legacy_passwd_format boolean NOT NULL,
    created timestamp with time zone NOT NULL,
    last_login timestamp with time zone,
    active boolean NOT NULL,
    activation_code character varying(255) NOT NULL,
    profile_complete boolean NOT NULL,
    newsletter boolean NOT NULL,
    acceptance boolean NOT NULL,
    promo_points integer NOT NULL,
    promo_multiplier numeric(6,2) NOT NULL,
    payment_deadline integer NOT NULL,
    req_for_opinion_sent date,
    r_client_num character varying(20) NOT NULL,
    promo_card_active boolean,
    client_hash character varying(32) NOT NULL
);


--
-- Name: main_client_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_client_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_client_id_seq OWNED BY main_client.id;


--
-- Name: main_clientcard; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_clientcard (
    id integer NOT NULL,
    client_id integer,
    number integer NOT NULL,
    activated timestamp with time zone,
    activation_code integer NOT NULL
);


--
-- Name: main_clientcard_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_clientcard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_clientcard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_clientcard_id_seq OWNED BY main_clientcard.id;


--
-- Name: main_clientdiscount; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_clientdiscount (
    id integer NOT NULL,
    nature character varying(16) NOT NULL,
    cover_variants boolean NOT NULL,
    net numeric(18,6) NOT NULL,
    gross numeric(18,6) NOT NULL,
    price_calc character varying(2) NOT NULL,
    percent numeric(6,2) NOT NULL,
    created timestamp with time zone NOT NULL,
    client_id integer NOT NULL,
    article_id integer NOT NULL
);


--
-- Name: main_clientdiscount_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_clientdiscount_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_clientdiscount_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_clientdiscount_id_seq OWNED BY main_clientdiscount.id;


--
-- Name: main_clientnumber; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_clientnumber (
    num integer NOT NULL,
    available boolean NOT NULL,
    date_taken timestamp with time zone
);


--
-- Name: main_company; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_company (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    addr_street character varying(255) NOT NULL,
    addr_town character varying(255) NOT NULL,
    addr_code character varying(255) NOT NULL,
    account_bank character varying(255) NOT NULL,
    account_no character varying(255) NOT NULL
);


--
-- Name: main_company_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_company_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_company_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_company_id_seq OWNED BY main_company.id;


--
-- Name: main_counter; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_counter (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    value integer NOT NULL
);


--
-- Name: main_counter_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_counter_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_counter_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_counter_id_seq OWNED BY main_counter.id;


--
-- Name: main_executiontime; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_executiontime (
    id integer NOT NULL,
    min integer NOT NULL,
    max integer NOT NULL
);


--
-- Name: main_executiontime_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_executiontime_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_executiontime_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_executiontime_id_seq OWNED BY main_executiontime.id;


--
-- Name: main_file; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_file (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(255) NOT NULL,
    file character varying(100) NOT NULL
);


--
-- Name: main_file_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_file_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_file_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_file_id_seq OWNED BY main_file.id;


--
-- Name: main_filetype; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_filetype (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    icon character varying(100) NOT NULL
);


--
-- Name: main_filetype_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_filetype_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_filetype_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_filetype_id_seq OWNED BY main_filetype.id;


--
-- Name: main_helplink; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_helplink (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    url character varying(255) NOT NULL
);


--
-- Name: main_helplink_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_helplink_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_helplink_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_helplink_id_seq OWNED BY main_helplink.id;


--
-- Name: main_invoiceaddress; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_invoiceaddress (
    id integer NOT NULL,
    type character varying(1) NOT NULL,
    first_name character varying(80) NOT NULL,
    last_name character varying(80) NOT NULL,
    company_name character varying(80) NOT NULL,
    nip character varying(255) NOT NULL,
    town character varying(255) NOT NULL,
    street character varying(255) NOT NULL,
    number character varying(255) NOT NULL,
    code character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    second_phone character varying(255) NOT NULL
);


--
-- Name: main_invoiceaddress_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_invoiceaddress_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_invoiceaddress_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_invoiceaddress_id_seq OWNED BY main_invoiceaddress.id;


--
-- Name: main_logentry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_logentry (
    id integer NOT NULL,
    category character varying(50) NOT NULL,
    level character varying(50) NOT NULL,
    message text NOT NULL,
    created timestamp with time zone NOT NULL
);


--
-- Name: main_logentry_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_logentry_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_logentry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_logentry_id_seq OWNED BY main_logentry.id;


--
-- Name: main_mainpagead; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_mainpagead (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    "order" integer NOT NULL,
    target character varying(200) NOT NULL,
    file character varying(100) NOT NULL
);


--
-- Name: main_mainpagead_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_mainpagead_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_mainpagead_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_mainpagead_id_seq OWNED BY main_mainpagead.id;


--
-- Name: main_metainfo; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_metainfo (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(255) NOT NULL,
    content text NOT NULL
);


--
-- Name: main_metainfo_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_metainfo_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_metainfo_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_metainfo_id_seq OWNED BY main_metainfo.id;


--
-- Name: main_metaproducer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_metaproducer (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    prod_ids character varying(255) NOT NULL
);


--
-- Name: main_metaproducer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_metaproducer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_metaproducer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_metaproducer_id_seq OWNED BY main_metaproducer.id;


--
-- Name: main_news; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_news (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    public boolean NOT NULL,
    created date NOT NULL,
    sticky boolean NOT NULL,
    summary text NOT NULL,
    more_link character varying(255) NOT NULL
);


--
-- Name: main_news_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_news_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_news_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_news_id_seq OWNED BY main_news.id;


--
-- Name: main_opinion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_opinion (
    id integer NOT NULL,
    article_id integer NOT NULL,
    client_login character varying(255) NOT NULL,
    rating integer NOT NULL,
    content text NOT NULL,
    created timestamp with time zone NOT NULL,
    blocked boolean NOT NULL,
    abuse_count integer NOT NULL,
    author character varying(255) NOT NULL
);


--
-- Name: main_opinion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_opinion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_opinion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_opinion_id_seq OWNED BY main_opinion.id;


--
-- Name: main_order; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_order (
    cart_ptr_id integer NOT NULL,
    invoice_address_id integer NOT NULL,
    submitted boolean NOT NULL,
    number character varying(80) NOT NULL,
    stock_id integer,
    stock_number character varying(255) NOT NULL,
    status character varying(2) NOT NULL,
    created timestamp with time zone NOT NULL,
    execution_date date,
    payment character varying(2) NOT NULL,
    payment_amount numeric(18,2),
    payment_status character varying(2) NOT NULL,
    payment_trans_num character varying(255) NOT NULL,
    payment_deadline date,
    suspended boolean NOT NULL,
    comments text NOT NULL,
    sent_to_supplier_id integer,
    inv_client character varying(100),
    inv_perfekt character varying(100)
);


--
-- Name: main_orderitem; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_orderitem (
    id integer NOT NULL,
    article_id integer NOT NULL,
    qty numeric(10,4) NOT NULL,
    param_value text NOT NULL,
    created timestamp with time zone NOT NULL,
    cat_index character varying(255) NOT NULL,
    stock_id integer,
    name character varying(255) NOT NULL,
    variant boolean NOT NULL,
    variants_name character varying(255) NOT NULL,
    variant_name character varying(255) NOT NULL,
    unit_short character varying(255) NOT NULL,
    unit_precision numeric(8,4) NOT NULL,
    param boolean NOT NULL,
    param_name character varying(255) NOT NULL,
    param_name_plural character varying(255) NOT NULL,
    weight numeric(14,4) NOT NULL,
    orig_net numeric(18,6) NOT NULL,
    orig_gross numeric(18,6) NOT NULL,
    discount_net numeric(18,6) NOT NULL,
    discount_gross numeric(18,6) NOT NULL,
    owner_id integer NOT NULL,
    discount_price_calc character varying(2)
);


--
-- Name: main_orderitem_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_orderitem_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_orderitem_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_orderitem_id_seq OWNED BY main_orderitem.id;


--
-- Name: main_ordernote; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_ordernote (
    id integer NOT NULL,
    order_id integer NOT NULL,
    created timestamp with time zone NOT NULL,
    content text NOT NULL
);


--
-- Name: main_ordernote_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_ordernote_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_ordernote_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_ordernote_id_seq OWNED BY main_ordernote.id;


--
-- Name: main_pagefragment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_pagefragment (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    location character varying(50) NOT NULL,
    "order" integer,
    content text NOT NULL
);


--
-- Name: main_pagefragment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_pagefragment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_pagefragment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_pagefragment_id_seq OWNED BY main_pagefragment.id;


--
-- Name: main_pagefragmentattachment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_pagefragmentattachment (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    file character varying(100) NOT NULL
);


--
-- Name: main_pagefragmentattachment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_pagefragmentattachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_pagefragmentattachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_pagefragmentattachment_id_seq OWNED BY main_pagefragmentattachment.id;


--
-- Name: main_producer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_producer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_producer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_producer_id_seq OWNED BY main_producer.id;


--
-- Name: main_promotion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_promotion_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_promotion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_promotion_id_seq OWNED BY main_promotion.id;


--
-- Name: main_property; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_property (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    "desc" text NOT NULL
);


--
-- Name: main_property_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_property_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_property_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_property_id_seq OWNED BY main_property.id;


--
-- Name: main_propertymembership; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_propertymembership (
    id integer NOT NULL,
    prop_id integer NOT NULL,
    spec_id integer NOT NULL,
    "order" integer NOT NULL
);


--
-- Name: main_propertymembership_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_propertymembership_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_propertymembership_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_propertymembership_id_seq OWNED BY main_propertymembership.id;


--
-- Name: main_redirect; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_redirect (
    id integer NOT NULL,
    source character varying(255) NOT NULL,
    dest character varying(255) NOT NULL
);


--
-- Name: main_redirect_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_redirect_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_redirect_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_redirect_id_seq OWNED BY main_redirect.id;


--
-- Name: main_shipment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shipment (
    id integer NOT NULL,
    type character varying(1) NOT NULL,
    first_name character varying(80) NOT NULL,
    last_name character varying(80) NOT NULL,
    company_name character varying(80) NOT NULL,
    nip character varying(255) NOT NULL,
    town character varying(255) NOT NULL,
    street character varying(255) NOT NULL,
    number character varying(255) NOT NULL,
    code character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    second_phone character varying(255) NOT NULL,
    order_id integer NOT NULL,
    auto_shipper boolean NOT NULL,
    auto_params boolean NOT NULL,
    pkg_type character varying(6) NOT NULL,
    pkg_count integer NOT NULL,
    shipper_name character varying(255) NOT NULL,
    identifier character varying(255) NOT NULL,
    sent timestamp with time zone,
    net numeric(18,6) NOT NULL,
    gross numeric(18,6) NOT NULL,
    discount_net numeric(18,6) NOT NULL,
    discount_gross numeric(18,6) NOT NULL,
    price_calc character varying(2) NOT NULL
);


--
-- Name: main_shipment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shipment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shipment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shipment_id_seq OWNED BY main_shipment.id;


--
-- Name: main_shipper; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shipper (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    invoice_name character varying(255) NOT NULL,
    vat numeric(6,2) NOT NULL,
    shipment_tracking_url character varying(200) NOT NULL,
    packages boolean NOT NULL,
    package_wrapping_weight numeric(8,4),
    pallets boolean NOT NULL,
    pallet_capacity numeric(8,2),
    cash_on_delivery boolean NOT NULL,
    cash_on_delivery_net numeric(18,6),
    "order" integer,
    category character varying(255)
);


--
-- Name: main_shipper_excluded_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shipper_excluded_categories (
    id integer NOT NULL,
    shipper_id integer NOT NULL,
    category_id integer NOT NULL
);


--
-- Name: main_shipper_excluded_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shipper_excluded_categories_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shipper_excluded_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shipper_excluded_categories_id_seq OWNED BY main_shipper_excluded_categories.id;


--
-- Name: main_shipper_excluded_producers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shipper_excluded_producers (
    id integer NOT NULL,
    shipper_id integer NOT NULL,
    producer_id integer NOT NULL
);


--
-- Name: main_shipper_excluded_producers_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shipper_excluded_producers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shipper_excluded_producers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shipper_excluded_producers_id_seq OWNED BY main_shipper_excluded_producers.id;


--
-- Name: main_shipper_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shipper_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shipper_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shipper_id_seq OWNED BY main_shipper.id;


--
-- Name: main_shipperpackagethrl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shipperpackagethrl (
    id integer NOT NULL,
    max_weight numeric(8,2) NOT NULL,
    net numeric(18,6) NOT NULL,
    gross numeric(18,6) NOT NULL,
    price_calc character varying(2) NOT NULL,
    shipper_id integer NOT NULL
);


--
-- Name: main_shipperpackagethrl_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shipperpackagethrl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shipperpackagethrl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shipperpackagethrl_id_seq OWNED BY main_shipperpackagethrl.id;


--
-- Name: main_shipperpalletthrl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shipperpalletthrl (
    id integer NOT NULL,
    max_weight numeric(8,2) NOT NULL,
    net numeric(18,6) NOT NULL,
    gross numeric(18,6) NOT NULL,
    price_calc character varying(2) NOT NULL,
    shipper_id integer NOT NULL
);


--
-- Name: main_shipperpalletthrl_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shipperpalletthrl_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shipperpalletthrl_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shipperpalletthrl_id_seq OWNED BY main_shipperpalletthrl.id;


--
-- Name: main_shoparticle_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shoparticle_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shoparticle_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shoparticle_id_seq OWNED BY main_shoparticle.id;


--
-- Name: main_shoparticle_recc_articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_shoparticle_recc_articles (
    id integer NOT NULL,
    from_shoparticle_id integer NOT NULL,
    to_shoparticle_id integer NOT NULL
);


--
-- Name: main_shoparticle_recc_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_shoparticle_recc_articles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_shoparticle_recc_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_shoparticle_recc_articles_id_seq OWNED BY main_shoparticle_recc_articles.id;


--
-- Name: main_spageattachment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_spageattachment (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    name character varying(255) NOT NULL,
    file character varying(100) NOT NULL
);


--
-- Name: main_spageattachment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_spageattachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_spageattachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_spageattachment_id_seq OWNED BY main_spageattachment.id;


--
-- Name: main_spagecontent; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_spagecontent (
    id integer NOT NULL,
    owner_id integer NOT NULL,
    content text NOT NULL
);


--
-- Name: main_spagecontent_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_spagecontent_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_spagecontent_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_spagecontent_id_seq OWNED BY main_spagecontent.id;


--
-- Name: main_specification; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_specification (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


--
-- Name: main_specification_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_specification_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_specification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_specification_id_seq OWNED BY main_specification.id;


--
-- Name: main_staticpage; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_staticpage (
    id integer NOT NULL,
    parent_id integer,
    title character varying(255) NOT NULL,
    public boolean NOT NULL,
    display_index boolean NOT NULL,
    backlink boolean NOT NULL,
    "order" integer NOT NULL,
    lft integer NOT NULL,
    rght integer NOT NULL,
    tree_id integer NOT NULL,
    level integer NOT NULL,
    CONSTRAINT main_staticpage_level_check CHECK ((level >= 0)),
    CONSTRAINT main_staticpage_lft_check CHECK ((lft >= 0)),
    CONSTRAINT main_staticpage_rght_check CHECK ((rght >= 0)),
    CONSTRAINT main_staticpage_tree_id_check CHECK ((tree_id >= 0))
);


--
-- Name: main_staticpage_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_staticpage_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_staticpage_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_staticpage_id_seq OWNED BY main_staticpage.id;


--
-- Name: main_stockintegration; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_stockintegration (
    id integer NOT NULL,
    supplier_id integer NOT NULL,
    provider character varying(50) NOT NULL,
    provider_ver character varying(255) NOT NULL,
    integrator_host character varying(50) NOT NULL
);


--
-- Name: main_stockintegration_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_stockintegration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_stockintegration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_stockintegration_id_seq OWNED BY main_stockintegration.id;


--
-- Name: main_supplier; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_supplier (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    phone character varying(255) NOT NULL,
    fax character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    internal_supplier boolean NOT NULL,
    exec_time_id integer,
    has_stock_integration boolean NOT NULL
);


--
-- Name: main_supplier_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_supplier_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_supplier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_supplier_id_seq OWNED BY main_supplier.id;


--
-- Name: main_systemparam; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_systemparam (
    id integer NOT NULL,
    key character varying(255) NOT NULL,
    value character varying(255) NOT NULL,
    help_text text NOT NULL
);


--
-- Name: main_systemparam_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_systemparam_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_systemparam_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_systemparam_id_seq OWNED BY main_systemparam.id;


--
-- Name: main_unit; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_unit (
    id integer NOT NULL,
    stock_id integer,
    name character varying(255) NOT NULL,
    name_accusative character varying(255) NOT NULL,
    short character varying(255) NOT NULL,
    "precision" numeric(8,4) NOT NULL
);


--
-- Name: main_unit_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_unit_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_unit_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_unit_id_seq OWNED BY main_unit.id;


--
-- Name: main_userprofile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE main_userprofile (
    id integer NOT NULL,
    user_id integer NOT NULL,
    supplier_id integer NOT NULL
);


--
-- Name: main_userprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE main_userprofile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MAXVALUE
    NO MINVALUE
    CACHE 1;


--
-- Name: main_userprofile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE main_userprofile_id_seq OWNED BY main_userprofile.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group ALTER COLUMN id SET DEFAULT nextval('auth_group_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('auth_group_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_message ALTER COLUMN id SET DEFAULT nextval('auth_message_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission ALTER COLUMN id SET DEFAULT nextval('auth_permission_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user ALTER COLUMN id SET DEFAULT nextval('auth_user_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups ALTER COLUMN id SET DEFAULT nextval('auth_user_groups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('auth_user_user_permissions_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log ALTER COLUMN id SET DEFAULT nextval('django_admin_log_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_content_type ALTER COLUMN id SET DEFAULT nextval('django_content_type_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_site ALTER COLUMN id SET DEFAULT nextval('django_site_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_additionallink ALTER COLUMN id SET DEFAULT nextval('main_additionallink_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_address ALTER COLUMN id SET DEFAULT nextval('main_address_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_article ALTER COLUMN id SET DEFAULT nextval('main_article_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleattachment ALTER COLUMN id SET DEFAULT nextval('main_articleattachment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleparam ALTER COLUMN id SET DEFAULT nextval('main_articleparam_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlephoto ALTER COLUMN id SET DEFAULT nextval('main_articlephoto_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleproperty ALTER COLUMN id SET DEFAULT nextval('main_articleproperty_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevariant ALTER COLUMN id SET DEFAULT nextval('main_articlevariant_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevideo ALTER COLUMN id SET DEFAULT nextval('main_articlevideo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_cart ALTER COLUMN id SET DEFAULT nextval('main_cart_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_cartitem ALTER COLUMN id SET DEFAULT nextval('main_cartitem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_category ALTER COLUMN id SET DEFAULT nextval('main_category_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_client ALTER COLUMN id SET DEFAULT nextval('main_client_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientcard ALTER COLUMN id SET DEFAULT nextval('main_clientcard_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientdiscount ALTER COLUMN id SET DEFAULT nextval('main_clientdiscount_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_company ALTER COLUMN id SET DEFAULT nextval('main_company_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_counter ALTER COLUMN id SET DEFAULT nextval('main_counter_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_executiontime ALTER COLUMN id SET DEFAULT nextval('main_executiontime_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_file ALTER COLUMN id SET DEFAULT nextval('main_file_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_filetype ALTER COLUMN id SET DEFAULT nextval('main_filetype_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_helplink ALTER COLUMN id SET DEFAULT nextval('main_helplink_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_invoiceaddress ALTER COLUMN id SET DEFAULT nextval('main_invoiceaddress_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_logentry ALTER COLUMN id SET DEFAULT nextval('main_logentry_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_mainpagead ALTER COLUMN id SET DEFAULT nextval('main_mainpagead_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_metainfo ALTER COLUMN id SET DEFAULT nextval('main_metainfo_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_metaproducer ALTER COLUMN id SET DEFAULT nextval('main_metaproducer_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_news ALTER COLUMN id SET DEFAULT nextval('main_news_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_opinion ALTER COLUMN id SET DEFAULT nextval('main_opinion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_orderitem ALTER COLUMN id SET DEFAULT nextval('main_orderitem_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_ordernote ALTER COLUMN id SET DEFAULT nextval('main_ordernote_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_pagefragment ALTER COLUMN id SET DEFAULT nextval('main_pagefragment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_pagefragmentattachment ALTER COLUMN id SET DEFAULT nextval('main_pagefragmentattachment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_producer ALTER COLUMN id SET DEFAULT nextval('main_producer_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_promotion ALTER COLUMN id SET DEFAULT nextval('main_promotion_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_property ALTER COLUMN id SET DEFAULT nextval('main_property_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_propertymembership ALTER COLUMN id SET DEFAULT nextval('main_propertymembership_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_redirect ALTER COLUMN id SET DEFAULT nextval('main_redirect_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipment ALTER COLUMN id SET DEFAULT nextval('main_shipment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper ALTER COLUMN id SET DEFAULT nextval('main_shipper_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_categories ALTER COLUMN id SET DEFAULT nextval('main_shipper_excluded_categories_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_producers ALTER COLUMN id SET DEFAULT nextval('main_shipper_excluded_producers_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpackagethrl ALTER COLUMN id SET DEFAULT nextval('main_shipperpackagethrl_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpalletthrl ALTER COLUMN id SET DEFAULT nextval('main_shipperpalletthrl_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle ALTER COLUMN id SET DEFAULT nextval('main_shoparticle_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle_recc_articles ALTER COLUMN id SET DEFAULT nextval('main_shoparticle_recc_articles_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spageattachment ALTER COLUMN id SET DEFAULT nextval('main_spageattachment_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spagecontent ALTER COLUMN id SET DEFAULT nextval('main_spagecontent_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_specification ALTER COLUMN id SET DEFAULT nextval('main_specification_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_staticpage ALTER COLUMN id SET DEFAULT nextval('main_staticpage_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_stockintegration ALTER COLUMN id SET DEFAULT nextval('main_stockintegration_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_supplier ALTER COLUMN id SET DEFAULT nextval('main_supplier_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_systemparam ALTER COLUMN id SET DEFAULT nextval('main_systemparam_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_unit ALTER COLUMN id SET DEFAULT nextval('main_unit_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_userprofile ALTER COLUMN id SET DEFAULT nextval('main_userprofile_id_seq'::regclass);


--
-- Name: auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions_group_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_key UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_message_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_pkey PRIMARY KEY (id);


--
-- Name: auth_permission_content_type_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_key UNIQUE (content_type_id, codename);


--
-- Name: auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_key UNIQUE (user_id, group_id);


--
-- Name: auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_key UNIQUE (user_id, permission_id);


--
-- Name: auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type_app_label_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_app_label_key UNIQUE (app_label, model);


--
-- Name: django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: django_site_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_site
    ADD CONSTRAINT django_site_pkey PRIMARY KEY (id);


--
-- Name: main_additionallink_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_additionallink
    ADD CONSTRAINT main_additionallink_pkey PRIMARY KEY (id);


--
-- Name: main_address_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_address
    ADD CONSTRAINT main_address_pkey PRIMARY KEY (id);


--
-- Name: main_article_cat_index_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_article
    ADD CONSTRAINT main_article_cat_index_key UNIQUE (cat_index);


--
-- Name: main_article_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_article
    ADD CONSTRAINT main_article_pkey PRIMARY KEY (id);


--
-- Name: main_article_stock_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_article
    ADD CONSTRAINT main_article_stock_id_key UNIQUE (stock_id);


--
-- Name: main_articleattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleattachment
    ADD CONSTRAINT main_articleattachment_pkey PRIMARY KEY (id);


--
-- Name: main_articleparam_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleparam
    ADD CONSTRAINT main_articleparam_name_key UNIQUE (name);


--
-- Name: main_articleparam_name_plural_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleparam
    ADD CONSTRAINT main_articleparam_name_plural_key UNIQUE (name_plural);


--
-- Name: main_articleparam_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleparam
    ADD CONSTRAINT main_articleparam_pkey PRIMARY KEY (id);


--
-- Name: main_articlephoto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlephoto
    ADD CONSTRAINT main_articlephoto_pkey PRIMARY KEY (id);


--
-- Name: main_articleproperty_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleproperty
    ADD CONSTRAINT main_articleproperty_pkey PRIMARY KEY (id);


--
-- Name: main_articlevariant_article_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevariant
    ADD CONSTRAINT main_articlevariant_article_id_key UNIQUE (article_id);


--
-- Name: main_articlevariant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevariant
    ADD CONSTRAINT main_articlevariant_pkey PRIMARY KEY (id);


--
-- Name: main_articlevideo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevideo
    ADD CONSTRAINT main_articlevideo_pkey PRIMARY KEY (id);


--
-- Name: main_cart_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_cart
    ADD CONSTRAINT main_cart_pkey PRIMARY KEY (id);


--
-- Name: main_cartitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_cartitem
    ADD CONSTRAINT main_cartitem_pkey PRIMARY KEY (id);


--
-- Name: main_category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_category
    ADD CONSTRAINT main_category_pkey PRIMARY KEY (id);


--
-- Name: main_client_client_num_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_client
    ADD CONSTRAINT main_client_client_num_key UNIQUE (client_num);


--
-- Name: main_client_login_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_client
    ADD CONSTRAINT main_client_login_key UNIQUE (login);


--
-- Name: main_client_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_client
    ADD CONSTRAINT main_client_pkey PRIMARY KEY (id);


--
-- Name: main_client_r_client_num_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_client
    ADD CONSTRAINT main_client_r_client_num_key UNIQUE (r_client_num);


--
-- Name: main_client_stock_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_client
    ADD CONSTRAINT main_client_stock_id_key UNIQUE (stock_id);


--
-- Name: main_clientcard_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientcard
    ADD CONSTRAINT main_clientcard_number_key UNIQUE (number);


--
-- Name: main_clientcard_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientcard
    ADD CONSTRAINT main_clientcard_pkey PRIMARY KEY (id);


--
-- Name: main_clientdiscount_client_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientdiscount
    ADD CONSTRAINT main_clientdiscount_client_id_key UNIQUE (client_id, article_id);


--
-- Name: main_clientdiscount_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientdiscount
    ADD CONSTRAINT main_clientdiscount_pkey PRIMARY KEY (id);


--
-- Name: main_clientnumber_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientnumber
    ADD CONSTRAINT main_clientnumber_pkey PRIMARY KEY (num);


--
-- Name: main_company_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_company
    ADD CONSTRAINT main_company_pkey PRIMARY KEY (id);


--
-- Name: main_counter_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_counter
    ADD CONSTRAINT main_counter_name_key UNIQUE (name);


--
-- Name: main_counter_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_counter
    ADD CONSTRAINT main_counter_pkey PRIMARY KEY (id);


--
-- Name: main_executiontime_min_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_executiontime
    ADD CONSTRAINT main_executiontime_min_key UNIQUE (min, max);


--
-- Name: main_executiontime_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_executiontime
    ADD CONSTRAINT main_executiontime_pkey PRIMARY KEY (id);


--
-- Name: main_file_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_file
    ADD CONSTRAINT main_file_name_key UNIQUE (name);


--
-- Name: main_file_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_file
    ADD CONSTRAINT main_file_pkey PRIMARY KEY (id);


--
-- Name: main_filetype_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_filetype
    ADD CONSTRAINT main_filetype_name_key UNIQUE (name);


--
-- Name: main_filetype_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_filetype
    ADD CONSTRAINT main_filetype_pkey PRIMARY KEY (id);


--
-- Name: main_helplink_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_helplink
    ADD CONSTRAINT main_helplink_name_key UNIQUE (name);


--
-- Name: main_helplink_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_helplink
    ADD CONSTRAINT main_helplink_pkey PRIMARY KEY (id);


--
-- Name: main_invoiceaddress_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_invoiceaddress
    ADD CONSTRAINT main_invoiceaddress_pkey PRIMARY KEY (id);


--
-- Name: main_logentry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_logentry
    ADD CONSTRAINT main_logentry_pkey PRIMARY KEY (id);


--
-- Name: main_mainpagead_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_mainpagead
    ADD CONSTRAINT main_mainpagead_pkey PRIMARY KEY (id);


--
-- Name: main_metainfo_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_metainfo
    ADD CONSTRAINT main_metainfo_pkey PRIMARY KEY (id);


--
-- Name: main_metaproducer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_metaproducer
    ADD CONSTRAINT main_metaproducer_pkey PRIMARY KEY (id);


--
-- Name: main_news_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_news
    ADD CONSTRAINT main_news_pkey PRIMARY KEY (id);


--
-- Name: main_opinion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_opinion
    ADD CONSTRAINT main_opinion_pkey PRIMARY KEY (id);


--
-- Name: main_order_invoice_address_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT main_order_invoice_address_id_key UNIQUE (invoice_address_id);


--
-- Name: main_order_number_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT main_order_number_key UNIQUE (number);


--
-- Name: main_order_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT main_order_pkey PRIMARY KEY (cart_ptr_id);


--
-- Name: main_order_stock_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT main_order_stock_id_key UNIQUE (stock_id);


--
-- Name: main_orderitem_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_orderitem
    ADD CONSTRAINT main_orderitem_pkey PRIMARY KEY (id);


--
-- Name: main_ordernote_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_ordernote
    ADD CONSTRAINT main_ordernote_pkey PRIMARY KEY (id);


--
-- Name: main_pagefragment_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_pagefragment
    ADD CONSTRAINT main_pagefragment_name_key UNIQUE (name);


--
-- Name: main_pagefragment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_pagefragment
    ADD CONSTRAINT main_pagefragment_pkey PRIMARY KEY (id);


--
-- Name: main_pagefragmentattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_pagefragmentattachment
    ADD CONSTRAINT main_pagefragmentattachment_pkey PRIMARY KEY (id);


--
-- Name: main_producer_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_producer
    ADD CONSTRAINT main_producer_name_key UNIQUE (name);


--
-- Name: main_producer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_producer
    ADD CONSTRAINT main_producer_pkey PRIMARY KEY (id);


--
-- Name: main_promotion_article_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_promotion
    ADD CONSTRAINT main_promotion_article_id_key UNIQUE (article_id);


--
-- Name: main_promotion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_promotion
    ADD CONSTRAINT main_promotion_pkey PRIMARY KEY (id);


--
-- Name: main_property_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_property
    ADD CONSTRAINT main_property_name_key UNIQUE (name);


--
-- Name: main_property_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_property
    ADD CONSTRAINT main_property_pkey PRIMARY KEY (id);


--
-- Name: main_propertymembership_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_propertymembership
    ADD CONSTRAINT main_propertymembership_pkey PRIMARY KEY (id);


--
-- Name: main_redirect_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_redirect
    ADD CONSTRAINT main_redirect_pkey PRIMARY KEY (id);


--
-- Name: main_redirect_source_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_redirect
    ADD CONSTRAINT main_redirect_source_key UNIQUE (source);


--
-- Name: main_shipment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipment
    ADD CONSTRAINT main_shipment_pkey PRIMARY KEY (id);


--
-- Name: main_shipper_excluded_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_categories
    ADD CONSTRAINT main_shipper_excluded_categories_pkey PRIMARY KEY (id);


--
-- Name: main_shipper_excluded_categories_shipper_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_categories
    ADD CONSTRAINT main_shipper_excluded_categories_shipper_id_key UNIQUE (shipper_id, category_id);


--
-- Name: main_shipper_excluded_producers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_producers
    ADD CONSTRAINT main_shipper_excluded_producers_pkey PRIMARY KEY (id);


--
-- Name: main_shipper_excluded_producers_shipper_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_producers
    ADD CONSTRAINT main_shipper_excluded_producers_shipper_id_key UNIQUE (shipper_id, producer_id);


--
-- Name: main_shipper_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper
    ADD CONSTRAINT main_shipper_name_key UNIQUE (name);


--
-- Name: main_shipper_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper
    ADD CONSTRAINT main_shipper_pkey PRIMARY KEY (id);


--
-- Name: main_shipperpackagethrl_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpackagethrl
    ADD CONSTRAINT main_shipperpackagethrl_pkey PRIMARY KEY (id);


--
-- Name: main_shipperpackagethrl_shipper_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpackagethrl
    ADD CONSTRAINT main_shipperpackagethrl_shipper_id_key UNIQUE (shipper_id, max_weight);


--
-- Name: main_shipperpalletthrl_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpalletthrl
    ADD CONSTRAINT main_shipperpalletthrl_pkey PRIMARY KEY (id);


--
-- Name: main_shipperpalletthrl_shipper_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpalletthrl
    ADD CONSTRAINT main_shipperpalletthrl_shipper_id_key UNIQUE (shipper_id, max_weight);


--
-- Name: main_shoparticle_article_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_article_id_key UNIQUE (article_id);


--
-- Name: main_shoparticle_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_pkey PRIMARY KEY (id);


--
-- Name: main_shoparticle_recc_articles_from_shoparticle_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle_recc_articles
    ADD CONSTRAINT main_shoparticle_recc_articles_from_shoparticle_id_key UNIQUE (from_shoparticle_id, to_shoparticle_id);


--
-- Name: main_shoparticle_recc_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle_recc_articles
    ADD CONSTRAINT main_shoparticle_recc_articles_pkey PRIMARY KEY (id);


--
-- Name: main_spageattachment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spageattachment
    ADD CONSTRAINT main_spageattachment_pkey PRIMARY KEY (id);


--
-- Name: main_spagecontent_owner_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spagecontent
    ADD CONSTRAINT main_spagecontent_owner_id_key UNIQUE (owner_id);


--
-- Name: main_spagecontent_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spagecontent
    ADD CONSTRAINT main_spagecontent_pkey PRIMARY KEY (id);


--
-- Name: main_specification_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_specification
    ADD CONSTRAINT main_specification_name_key UNIQUE (name);


--
-- Name: main_specification_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_specification
    ADD CONSTRAINT main_specification_pkey PRIMARY KEY (id);


--
-- Name: main_staticpage_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_staticpage
    ADD CONSTRAINT main_staticpage_pkey PRIMARY KEY (id);


--
-- Name: main_stockintegration_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_stockintegration
    ADD CONSTRAINT main_stockintegration_pkey PRIMARY KEY (id);


--
-- Name: main_supplier_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_supplier
    ADD CONSTRAINT main_supplier_name_key UNIQUE (name);


--
-- Name: main_supplier_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_supplier
    ADD CONSTRAINT main_supplier_pkey PRIMARY KEY (id);


--
-- Name: main_systemparam_key_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_systemparam
    ADD CONSTRAINT main_systemparam_key_key UNIQUE (key);


--
-- Name: main_systemparam_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_systemparam
    ADD CONSTRAINT main_systemparam_pkey PRIMARY KEY (id);


--
-- Name: main_unit_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_unit
    ADD CONSTRAINT main_unit_name_key UNIQUE (name);


--
-- Name: main_unit_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_unit
    ADD CONSTRAINT main_unit_pkey PRIMARY KEY (id);


--
-- Name: main_unit_short_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_unit
    ADD CONSTRAINT main_unit_short_key UNIQUE (short);


--
-- Name: main_userprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT main_userprofile_pkey PRIMARY KEY (id);


--
-- Name: main_userprofile_user_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT main_userprofile_user_id_key UNIQUE (user_id);


--
-- Name: auth_group_permissions_group_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_group_id ON auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_group_permissions_permission_id ON auth_group_permissions USING btree (permission_id);


--
-- Name: auth_message_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_message_user_id ON auth_message USING btree (user_id);


--
-- Name: auth_permission_content_type_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_permission_content_type_id ON auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_groups_group_id ON auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_groups_user_id ON auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_user_permissions_permission_id ON auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX auth_user_user_permissions_user_id ON auth_user_user_permissions USING btree (user_id);


--
-- Name: django_admin_log_content_type_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_content_type_id ON django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX django_admin_log_user_id ON django_admin_log USING btree (user_id);


--
-- Name: main_address_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_client_id ON main_address USING btree (client_id);


--
-- Name: main_address_company_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_company_name ON main_address USING btree (company_name);


--
-- Name: main_address_company_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_company_name_like ON main_address USING btree (company_name varchar_pattern_ops);


--
-- Name: main_address_first_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_first_name ON main_address USING btree (first_name);


--
-- Name: main_address_first_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_first_name_like ON main_address USING btree (first_name varchar_pattern_ops);


--
-- Name: main_address_last_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_last_name ON main_address USING btree (last_name);


--
-- Name: main_address_last_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_address_last_name_like ON main_address USING btree (last_name varchar_pattern_ops);


--
-- Name: main_article_unit_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_article_unit_id ON main_article USING btree (unit_id);


--
-- Name: main_articleattachment_article_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articleattachment_article_id ON main_articleattachment USING btree (article_id);


--
-- Name: main_articleattachment_type_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articleattachment_type_id ON main_articleattachment USING btree (type_id);


--
-- Name: main_articlephoto_article_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articlephoto_article_id ON main_articlephoto USING btree (article_id);


--
-- Name: main_articleproperty_article_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articleproperty_article_id ON main_articleproperty USING btree (article_id);


--
-- Name: main_articleproperty_property_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articleproperty_property_id ON main_articleproperty USING btree (property_id);


--
-- Name: main_articlevariant_exec_time_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articlevariant_exec_time_id ON main_articlevariant USING btree (exec_time_id);


--
-- Name: main_articlevariant_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_articlevariant_owner_id ON main_articlevariant USING btree (owner_id);


--
-- Name: main_cart_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_cart_client_id ON main_cart USING btree (client_id);


--
-- Name: main_cartitem_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_cartitem_owner_id ON main_cartitem USING btree (owner_id);


--
-- Name: main_category_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_level ON main_category USING btree (level);


--
-- Name: main_category_lft; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_lft ON main_category USING btree (lft);


--
-- Name: main_category_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_name ON main_category USING btree (name);


--
-- Name: main_category_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_name_like ON main_category USING btree (name varchar_pattern_ops);


--
-- Name: main_category_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_parent_id ON main_category USING btree (parent_id);


--
-- Name: main_category_rght; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_rght ON main_category USING btree (rght);


--
-- Name: main_category_tree_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_category_tree_id ON main_category USING btree (tree_id);


--
-- Name: main_client_company_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_client_company_name ON main_client USING btree (company_name);


--
-- Name: main_client_company_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_client_company_name_like ON main_client USING btree (company_name varchar_pattern_ops);


--
-- Name: main_client_first_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_client_first_name ON main_client USING btree (first_name);


--
-- Name: main_client_first_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_client_first_name_like ON main_client USING btree (first_name varchar_pattern_ops);


--
-- Name: main_client_last_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_client_last_name ON main_client USING btree (last_name);


--
-- Name: main_client_last_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_client_last_name_like ON main_client USING btree (last_name varchar_pattern_ops);


--
-- Name: main_clientcard_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_clientcard_client_id ON main_clientcard USING btree (client_id);


--
-- Name: main_clientdiscount_article_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_clientdiscount_article_id ON main_clientdiscount USING btree (article_id);


--
-- Name: main_clientdiscount_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_clientdiscount_client_id ON main_clientdiscount USING btree (client_id);


--
-- Name: main_clientnumber_available; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_clientnumber_available ON main_clientnumber USING btree (available);


--
-- Name: main_invoiceaddress_company_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_invoiceaddress_company_name ON main_invoiceaddress USING btree (company_name);


--
-- Name: main_invoiceaddress_company_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_invoiceaddress_company_name_like ON main_invoiceaddress USING btree (company_name varchar_pattern_ops);


--
-- Name: main_invoiceaddress_first_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_invoiceaddress_first_name ON main_invoiceaddress USING btree (first_name);


--
-- Name: main_invoiceaddress_first_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_invoiceaddress_first_name_like ON main_invoiceaddress USING btree (first_name varchar_pattern_ops);


--
-- Name: main_invoiceaddress_last_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_invoiceaddress_last_name ON main_invoiceaddress USING btree (last_name);


--
-- Name: main_invoiceaddress_last_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_invoiceaddress_last_name_like ON main_invoiceaddress USING btree (last_name varchar_pattern_ops);


--
-- Name: main_opinion_article_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_opinion_article_id ON main_opinion USING btree (article_id);


--
-- Name: main_order_created; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_created ON main_order USING btree (created);


--
-- Name: main_order_payment; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_payment ON main_order USING btree (payment);


--
-- Name: main_order_payment_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_payment_like ON main_order USING btree (payment varchar_pattern_ops);


--
-- Name: main_order_payment_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_payment_status ON main_order USING btree (payment_status);


--
-- Name: main_order_payment_status_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_payment_status_like ON main_order USING btree (payment_status varchar_pattern_ops);


--
-- Name: main_order_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_status ON main_order USING btree (status);


--
-- Name: main_order_status_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_status_like ON main_order USING btree (status varchar_pattern_ops);


--
-- Name: main_order_stock_number; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_stock_number ON main_order USING btree (stock_number);


--
-- Name: main_order_stock_number_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_stock_number_like ON main_order USING btree (stock_number varchar_pattern_ops);


--
-- Name: main_order_submitted; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_order_submitted ON main_order USING btree (submitted);


--
-- Name: main_orderitem_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_orderitem_owner_id ON main_orderitem USING btree (owner_id);


--
-- Name: main_ordernote_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_ordernote_order_id ON main_ordernote USING btree (order_id);


--
-- Name: main_pagefragment_location; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_pagefragment_location ON main_pagefragment USING btree (location);


--
-- Name: main_pagefragment_location_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_pagefragment_location_like ON main_pagefragment USING btree (location varchar_pattern_ops);


--
-- Name: main_pagefragmentattachment_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_pagefragmentattachment_owner_id ON main_pagefragmentattachment USING btree (owner_id);


--
-- Name: main_producer_exec_time_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_producer_exec_time_id ON main_producer USING btree (exec_time_id);


--
-- Name: main_propertymembership_prop_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_propertymembership_prop_id ON main_propertymembership USING btree (prop_id);


--
-- Name: main_propertymembership_spec_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_propertymembership_spec_id ON main_propertymembership USING btree (spec_id);


--
-- Name: main_shipment_company_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_company_name ON main_shipment USING btree (company_name);


--
-- Name: main_shipment_company_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_company_name_like ON main_shipment USING btree (company_name varchar_pattern_ops);


--
-- Name: main_shipment_first_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_first_name ON main_shipment USING btree (first_name);


--
-- Name: main_shipment_first_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_first_name_like ON main_shipment USING btree (first_name varchar_pattern_ops);


--
-- Name: main_shipment_last_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_last_name ON main_shipment USING btree (last_name);


--
-- Name: main_shipment_last_name_like; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_last_name_like ON main_shipment USING btree (last_name varchar_pattern_ops);


--
-- Name: main_shipment_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipment_order_id ON main_shipment USING btree (order_id);


--
-- Name: main_shipper_excluded_categories_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipper_excluded_categories_category_id ON main_shipper_excluded_categories USING btree (category_id);


--
-- Name: main_shipper_excluded_categories_shipper_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipper_excluded_categories_shipper_id ON main_shipper_excluded_categories USING btree (shipper_id);


--
-- Name: main_shipper_excluded_producers_producer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipper_excluded_producers_producer_id ON main_shipper_excluded_producers USING btree (producer_id);


--
-- Name: main_shipper_excluded_producers_shipper_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipper_excluded_producers_shipper_id ON main_shipper_excluded_producers USING btree (shipper_id);


--
-- Name: main_shipperpackagethrl_shipper_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipperpackagethrl_shipper_id ON main_shipperpackagethrl USING btree (shipper_id);


--
-- Name: main_shipperpalletthrl_shipper_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shipperpalletthrl_shipper_id ON main_shipperpalletthrl USING btree (shipper_id);


--
-- Name: main_shoparticle_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_category_id ON main_shoparticle USING btree (category_id);


--
-- Name: main_shoparticle_exec_time_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_exec_time_id ON main_shoparticle USING btree (exec_time_id);


--
-- Name: main_shoparticle_param_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_param_id ON main_shoparticle USING btree (param_id);


--
-- Name: main_shoparticle_producer_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_producer_id ON main_shoparticle USING btree (producer_id);


--
-- Name: main_shoparticle_recc_articles_from_shoparticle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_recc_articles_from_shoparticle_id ON main_shoparticle_recc_articles USING btree (from_shoparticle_id);


--
-- Name: main_shoparticle_recc_articles_to_shoparticle_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_recc_articles_to_shoparticle_id ON main_shoparticle_recc_articles USING btree (to_shoparticle_id);


--
-- Name: main_shoparticle_specification_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_specification_id ON main_shoparticle USING btree (specification_id);


--
-- Name: main_shoparticle_variants_unit_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_shoparticle_variants_unit_id ON main_shoparticle USING btree (variants_unit_id);


--
-- Name: main_spageattachment_owner_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_spageattachment_owner_id ON main_spageattachment USING btree (owner_id);


--
-- Name: main_staticpage_level; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_staticpage_level ON main_staticpage USING btree (level);


--
-- Name: main_staticpage_lft; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_staticpage_lft ON main_staticpage USING btree (lft);


--
-- Name: main_staticpage_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_staticpage_parent_id ON main_staticpage USING btree (parent_id);


--
-- Name: main_staticpage_rght; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_staticpage_rght ON main_staticpage USING btree (rght);


--
-- Name: main_staticpage_tree_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_staticpage_tree_id ON main_staticpage USING btree (tree_id);


--
-- Name: main_stockintegration_supplier_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_stockintegration_supplier_id ON main_stockintegration USING btree (supplier_id);


--
-- Name: main_userprofile_supplier_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX main_userprofile_supplier_id ON main_userprofile USING btree (supplier_id);


--
-- Name: article_id_refs_id_27aa9840; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleproperty
    ADD CONSTRAINT article_id_refs_id_27aa9840 FOREIGN KEY (article_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_message_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_message
    ADD CONSTRAINT auth_message_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups_group_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_fkey FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: client_id_refs_id_885a3e3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientcard
    ADD CONSTRAINT client_id_refs_id_885a3e3 FOREIGN KEY (client_id) REFERENCES main_client(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: client_id_refs_id_faf28769; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_address
    ADD CONSTRAINT client_id_refs_id_faf28769 FOREIGN KEY (client_id) REFERENCES main_client(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: content_type_id_refs_id_728de91f; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_permission
    ADD CONSTRAINT content_type_id_refs_id_728de91f FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_content_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_fkey FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: exec_time_id_refs_id_e60812f3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_producer
    ADD CONSTRAINT exec_time_id_refs_id_e60812f3 FOREIGN KEY (exec_time_id) REFERENCES main_executiontime(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: from_shoparticle_id_refs_id_1ea7bcd3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle_recc_articles
    ADD CONSTRAINT from_shoparticle_id_refs_id_1ea7bcd3 FOREIGN KEY (from_shoparticle_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: group_id_refs_id_3cea63fe; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_group_permissions
    ADD CONSTRAINT group_id_refs_id_3cea63fe FOREIGN KEY (group_id) REFERENCES auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: invoice_address_id_refs_id_53134175; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT invoice_address_id_refs_id_53134175 FOREIGN KEY (invoice_address_id) REFERENCES main_invoiceaddress(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_article_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_article
    ADD CONSTRAINT main_article_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES main_supplier(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_article_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_article
    ADD CONSTRAINT main_article_unit_id_fkey FOREIGN KEY (unit_id) REFERENCES main_unit(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_articleattachment_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleattachment
    ADD CONSTRAINT main_articleattachment_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_articlephoto_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlephoto
    ADD CONSTRAINT main_articlephoto_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_articleproperty_property_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleproperty
    ADD CONSTRAINT main_articleproperty_property_id_fkey FOREIGN KEY (property_id) REFERENCES main_propertymembership(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_articlevariant_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevariant
    ADD CONSTRAINT main_articlevariant_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_article(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_articlevariant_exec_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevariant
    ADD CONSTRAINT main_articlevariant_exec_time_id_fkey FOREIGN KEY (exec_time_id) REFERENCES main_executiontime(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_articlevariant_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articlevariant
    ADD CONSTRAINT main_articlevariant_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_cart_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_cart
    ADD CONSTRAINT main_cart_client_id_fkey FOREIGN KEY (client_id) REFERENCES main_client(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_cartitem_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_cartitem
    ADD CONSTRAINT main_cartitem_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES main_cart(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_clientdiscount_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientdiscount
    ADD CONSTRAINT main_clientdiscount_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_article(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_clientdiscount_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_clientdiscount
    ADD CONSTRAINT main_clientdiscount_client_id_fkey FOREIGN KEY (client_id) REFERENCES main_client(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_opinion_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_opinion
    ADD CONSTRAINT main_opinion_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_order_cart_ptr_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT main_order_cart_ptr_id_fkey FOREIGN KEY (cart_ptr_id) REFERENCES main_cart(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_order_sent_to_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_order
    ADD CONSTRAINT main_order_sent_to_supplier_id_fkey FOREIGN KEY (sent_to_supplier_id) REFERENCES main_supplier(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_orderitem_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_orderitem
    ADD CONSTRAINT main_orderitem_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES main_order(cart_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_ordernote_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_ordernote
    ADD CONSTRAINT main_ordernote_order_id_fkey FOREIGN KEY (order_id) REFERENCES main_order(cart_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_pagefragmentattachment_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_pagefragmentattachment
    ADD CONSTRAINT main_pagefragmentattachment_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES main_pagefragment(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_promotion_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_promotion
    ADD CONSTRAINT main_promotion_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_article(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_propertymembership_prop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_propertymembership
    ADD CONSTRAINT main_propertymembership_prop_id_fkey FOREIGN KEY (prop_id) REFERENCES main_property(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_propertymembership_spec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_propertymembership
    ADD CONSTRAINT main_propertymembership_spec_id_fkey FOREIGN KEY (spec_id) REFERENCES main_specification(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shipment_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipment
    ADD CONSTRAINT main_shipment_order_id_fkey FOREIGN KEY (order_id) REFERENCES main_order(cart_ptr_id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shipper_excluded_categories_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_categories
    ADD CONSTRAINT main_shipper_excluded_categories_category_id_fkey FOREIGN KEY (category_id) REFERENCES main_category(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shipper_excluded_producers_producer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_producers
    ADD CONSTRAINT main_shipper_excluded_producers_producer_id_fkey FOREIGN KEY (producer_id) REFERENCES main_producer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shipperpackagethrl_shipper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpackagethrl
    ADD CONSTRAINT main_shipperpackagethrl_shipper_id_fkey FOREIGN KEY (shipper_id) REFERENCES main_shipper(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shipperpalletthrl_shipper_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipperpalletthrl
    ADD CONSTRAINT main_shipperpalletthrl_shipper_id_fkey FOREIGN KEY (shipper_id) REFERENCES main_shipper(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_article_id_fkey FOREIGN KEY (article_id) REFERENCES main_article(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_category_id_fkey FOREIGN KEY (category_id) REFERENCES main_category(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_exec_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_exec_time_id_fkey FOREIGN KEY (exec_time_id) REFERENCES main_executiontime(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_param_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_param_id_fkey FOREIGN KEY (param_id) REFERENCES main_articleparam(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_producer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_producer_id_fkey FOREIGN KEY (producer_id) REFERENCES main_producer(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_specification_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_specification_id_fkey FOREIGN KEY (specification_id) REFERENCES main_specification(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_shoparticle_variants_unit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle
    ADD CONSTRAINT main_shoparticle_variants_unit_id_fkey FOREIGN KEY (variants_unit_id) REFERENCES main_unit(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_spageattachment_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spageattachment
    ADD CONSTRAINT main_spageattachment_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES main_staticpage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_spagecontent_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_spagecontent
    ADD CONSTRAINT main_spagecontent_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES main_staticpage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_stockintegration_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_stockintegration
    ADD CONSTRAINT main_stockintegration_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES main_supplier(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_supplier_exec_time_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_supplier
    ADD CONSTRAINT main_supplier_exec_time_id_fkey FOREIGN KEY (exec_time_id) REFERENCES main_executiontime(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: main_userprofile_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT main_userprofile_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: parent_id_refs_id_4a3cf3b3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_category
    ADD CONSTRAINT parent_id_refs_id_4a3cf3b3 FOREIGN KEY (parent_id) REFERENCES main_category(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: parent_id_refs_id_4e64a519; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_staticpage
    ADD CONSTRAINT parent_id_refs_id_4e64a519 FOREIGN KEY (parent_id) REFERENCES main_staticpage(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: shipper_id_refs_id_22120083; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_categories
    ADD CONSTRAINT shipper_id_refs_id_22120083 FOREIGN KEY (shipper_id) REFERENCES main_shipper(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: shipper_id_refs_id_aa58cbe7; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shipper_excluded_producers
    ADD CONSTRAINT shipper_id_refs_id_aa58cbe7 FOREIGN KEY (shipper_id) REFERENCES main_shipper(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: supplier_id_refs_id_a530654c; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_userprofile
    ADD CONSTRAINT supplier_id_refs_id_a530654c FOREIGN KEY (supplier_id) REFERENCES main_supplier(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: to_shoparticle_id_refs_id_1ea7bcd3; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_shoparticle_recc_articles
    ADD CONSTRAINT to_shoparticle_id_refs_id_1ea7bcd3 FOREIGN KEY (to_shoparticle_id) REFERENCES main_shoparticle(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: type_id_refs_id_f5bdc86b; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY main_articleattachment
    ADD CONSTRAINT type_id_refs_id_f5bdc86b FOREIGN KEY (type_id) REFERENCES main_filetype(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_831107f1; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_groups
    ADD CONSTRAINT user_id_refs_id_831107f1 FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: user_id_refs_id_f2045483; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY auth_user_user_permissions
    ADD CONSTRAINT user_id_refs_id_f2045483 FOREIGN KEY (user_id) REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

