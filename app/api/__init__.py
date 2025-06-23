async def get_db_session():
    from app.core.container import Container

    async with Container.async_session() as session:
        yield session
