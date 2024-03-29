const { SlashCommandBuilder } = require('@discordjs/builders')
const { EmbedBuilder } = require('discord.js')
const { lyricsExtractor } = require('@discord-player/extractor')
const { useMainPlayer } = require('discord-player')

module.exports = {
  data: new SlashCommandBuilder().setName('lyrics').
    setDescription('Gets the lyrics of the song'),
  async execute(interaction) {
    const player = useMainPlayer()
    const queue = player.nodes.get(interaction.guildId)
    const currentTrack = queue.currentTrack
    const lyricsFinder = lyricsExtractor(process.env.LYRICS_API_KEY)

    const lyrics = await lyricsFinder.search(currentTrack.title).
      catch(() => null)
    if (!lyrics) return interaction.reply(
      { content: 'No lyrics found', ephemeral: true })

    const trimmedLyrics = lyrics.lyrics.substring(0, 1997)

    const embed = new EmbedBuilder().setTitle(lyrics.title).
      setURL(lyrics.url).
      setThumbnail(lyrics.thumbnail).
      setAuthor({
        name: lyrics.artist.name,
        iconURL: lyrics.artist.image,
        url: lyrics.artist.url,
      }).
      setDescription(
        trimmedLyrics.length === 1997 ? `${trimmedLyrics}...` : trimmedLyrics).
      setColor('Yellow')

    return interaction.reply({ embeds: [embed] })
  },
}
