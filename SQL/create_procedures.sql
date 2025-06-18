CREATE PROCEDURE dbo.LogEchoClip
  @Filename   NVARCHAR(255),
  @ContextTag NVARCHAR(50)
AS
BEGIN
  INSERT INTO EchoClips (Filename, Timestamp, ContextTag)
  VALUES (@Filename, SYSUTCDATETIME(), @ContextTag);
END;
GO

git add SQL/create_procedures.sql
git commit -m "Add LogEchoClip stored procedure script"
git push